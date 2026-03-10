import numpy as np
import pytest
from pulsar.physics import System, Mass, Spring, Damper, Resistor, Inductor, Capacitor
from pulsar.dae_solver import DAESolver

def test_mechanical_system():
    sys = System(domain="mechanical")
    sys.add_component(Mass("m1", 2.0))
    sys.add_component(Spring("k1", 10.0))
    sys.add_component(Damper("c1", 1.5))

    A, B, C, D = sys.assemble()

    assert A.shape == (2, 2)
    assert B.shape == (2, 1)

    # Expected:
    # A = [[0, 1], [-10/2, -1.5/2]] = [[0, 1], [-5, -0.75]]
    # B = [[0], [1/2]] = [[0], [0.5]]
    np.testing.assert_array_equal(A, np.array([[0, 1], [-5, -0.75]]))
    np.testing.assert_array_equal(B, np.array([[0], [0.5]]))

def test_electrical_system():
    sys = System(domain="electrical")
    sys.add_component(Resistor("R1", 100.0))
    sys.add_component(Inductor("L1", 0.01))
    sys.add_component(Capacitor("C1", 0.001))

    A, B, C, D = sys.assemble()

    # A = [[0, 1/C], [-1/L, -R/L]] = [[0, 1000], [-100, -10000]]
    # B = [[0], [1/L]] = [[0], [100]]

    assert A.shape == (2, 2)
    assert B.shape == (2, 1)

    np.testing.assert_allclose(A, np.array([[0, 1000], [-100, -10000]]))
    np.testing.assert_allclose(B, np.array([[0], [100]]))

def test_dae_solver():
    A = np.array([[0, 1], [-5, -0.75]])
    B = np.array([[0], [0.5]])
    C = np.array([[1, 0]])
    D = np.array([[0]])

    solver = DAESolver(A, B, C, D)

    def u_func(t):
        return 1.0 # step input

    t_span = (0, 10)
    x0 = np.array([0, 0])

    t, x, y = solver.solve(t_span, u_func, x0)

    assert len(t) > 0
    assert x.shape == (2, len(t))
    assert y.shape == (1, len(t))
