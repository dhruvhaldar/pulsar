import numpy as np
from scipy.integrate import solve_ivp

class DAESolver:
    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def solve(self, t_span, u_func, x0, method='BDF', max_step=0.1):
        """
        Solve \dot{x} = Ax + Bu
        y = Cx + Du
        """
        def dxdt(t, x):
            # Reshape x to column vector just in case
            x = x.reshape(-1, 1)
            u = u_func(t)
            if np.isscalar(u):
                u = np.array([[u]])
            else:
                u = u.reshape(-1, 1)

            dx = self.A @ x + self.B @ u
            return dx.flatten()

        sol = solve_ivp(dxdt, t_span, x0, method=method, max_step=max_step)

        # Calculate y
        t = sol.t
        y = np.zeros((self.C.shape[0], len(t)))
        for i, ti in enumerate(t):
            xi = sol.y[:, i].reshape(-1, 1)
            u_i = u_func(ti)
            if np.isscalar(u_i):
                u_i = np.array([[u_i]])
            else:
                u_i = u_i.reshape(-1, 1)
            yi = self.C @ xi + self.D @ u_i
            y[:, i] = yi.flatten()

        return sol.t, sol.y, y
