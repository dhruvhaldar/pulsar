import numpy as np
import pytest
from pulsar.identification import estimate_arx, simulate_arx
from pulsar.validation import auto_correlation, cross_correlation

def test_arx_estimation():
    # True system:
    # y(t) - 1.5 y(t-1) + 0.7 y(t-2) = 1.0 u(t-1) + 0.5 u(t-2)
    # a1 = -1.5, a2 = 0.7, b1 = 1.0, b2 = 0.5
    # na=2, nb=2, nk=1

    N = 1000
    u = np.random.randn(N)
    e = 0.01 * np.random.randn(N) # Low noise
    y = np.zeros(N)

    a1, a2 = -1.5, 0.7
    b1, b2 = 1.0, 0.5

    for t in range(2, N):
        y[t] = -a1 * y[t-1] - a2 * y[t-2] + b1 * u[t-1] + b2 * u[t-2] + e[t]

    theta_hat = estimate_arx(u, y, na=2, nb=2, nk=1)

    assert len(theta_hat) == 4
    np.testing.assert_allclose(theta_hat, [a1, a2, b1, b2], atol=0.05)

def test_arx_simulation():
    N = 100
    u = np.ones(N)

    a1, a2 = -1.5, 0.7
    b1, b2 = 1.0, 0.5
    theta = np.array([a1, a2, b1, b2])

    y_sim = simulate_arx(u, theta, na=2, nb=2, nk=1)

    assert len(y_sim) == N
    # First few should be zero
    assert y_sim[0] == 0

def test_validation():
    N = 500
    e = np.random.randn(N)
    u = np.random.randn(N)

    r_ee = auto_correlation(e, max_lag=20)
    assert len(r_ee) == 21
    assert np.isclose(r_ee[0], 1.0) # Normalized to 1

    r_ue = cross_correlation(u, e, max_lag=20)
    assert len(r_ue) == 41 # -20 to 20
