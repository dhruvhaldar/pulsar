from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import io
import csv

from pulsar.physics import System, Mass, Spring, Damper, Resistor, Inductor, Capacitor
from pulsar.dae_solver import DAESolver
from pulsar.identification import estimate_arx, simulate_arx
from pulsar.validation import auto_correlation

app = FastAPI()

# CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComponentDef(BaseModel):
    type: str
    name: str
    value: float

class SimulateRequest(BaseModel):
    domain: str
    components: list[ComponentDef]
    t_end: float = 10.0
    u_type: str = "step" # step, sine

@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    try:
        sys = System(domain=req.domain)
        for comp in req.components:
            if comp.type == "Mass": sys.add_component(Mass(comp.name, comp.value))
            elif comp.type == "Spring": sys.add_component(Spring(comp.name, comp.value))
            elif comp.type == "Damper": sys.add_component(Damper(comp.name, comp.value))
            elif comp.type == "Resistor": sys.add_component(Resistor(comp.name, comp.value))
            elif comp.type == "Inductor": sys.add_component(Inductor(comp.name, comp.value))
            elif comp.type == "Capacitor": sys.add_component(Capacitor(comp.name, comp.value))

        A, B, C, D = sys.assemble()
        solver = DAESolver(A, B, C, D)

        def u_func(t):
            if req.u_type == "sine":
                return np.sin(t)
            return 1.0 # step

        t_span = (0, req.t_end)
        x0 = np.zeros(A.shape[0])

        t, x, y = solver.solve(t_span, u_func, x0)

        return {
            "t": t.tolist(),
            "y": y[0].tolist(),
            "u": [u_func(ti) for ti in t]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/identify")
async def identify(
    file: UploadFile = File(...),
    na: int = Form(2),
    nb: int = Form(2),
    nk: int = Form(1)
):
    try:
        # Read CSV file (time, input, output)
        content = await file.read()
        decoded = content.decode('utf-8')

        reader = csv.reader(io.StringIO(decoded))

        # Skip header if present
        data = list(reader)
        try:
            float(data[0][0])
        except ValueError:
            data = data[1:]

        u = np.array([float(row[1]) for row in data])
        y = np.array([float(row[2]) for row in data])
        t = np.array([float(row[0]) for row in data])

        # Estimate
        theta = estimate_arx(u, y, na, nb, nk)

        # Simulate
        y_sim = simulate_arx(u, theta, na, nb, nk)

        # Validation
        e = y - y_sim
        r_ee = auto_correlation(e, max_lag=20)

        # Compute Bode plot (simple approximation by evaluating frequency response)
        # H(e^{j w}) = B(e^{j w}) / A(e^{j w})
        # Note: B has delay nk
        a_params = theta[:na]
        b_params = theta[na:na+nb]

        w = np.logspace(-2, np.pi, 100) # frequency rad/sample

        mag = []
        phase = []

        for wi in w:
            z = np.exp(1j * wi)

            # A(z) = 1 + a1 z^-1 + ... + ana z^-na
            A_z = 1.0
            for i in range(1, na + 1):
                A_z += a_params[i-1] * (z ** -i)

            # B(z) = b1 z^-nk + ... + bnb z^-(nk+nb-1)
            B_z = 0.0
            for j in range(1, nb + 1):
                B_z += b_params[j-1] * (z ** -(nk + j - 1))

            H_z = B_z / A_z
            mag.append(float(np.abs(H_z)))
            phase.append(float(np.angle(H_z, deg=True)))

        return {
            "theta": theta.tolist(),
            "bode": {
                "w": w.tolist(),
                "mag": mag,
                "phase": phase
            },
            "validation": {
                "lags": list(range(len(r_ee))),
                "r_ee": r_ee.tolist()
            },
            "simulation": {
                "t": t.tolist(),
                "y": y.tolist(),
                "y_sim": y_sim.tolist()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
