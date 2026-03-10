import numpy as np

def estimate_arx(u, y, na, nb, nk):
    """
    Estimate ARX model parameters using OLS.
    A(q) y(t) = B(q) u(t - nk) + e(t)
    u: input array
    y: output array
    na: order of A polynomial (number of poles)
    nb: order of B polynomial (number of zeros + 1)
    nk: input delay

    Returns parameter vector theta [a_1, ..., a_na, b_1, ..., b_nb]
    """
    N = len(y)

    # Check max delay
    max_delay = max(na, nb + nk - 1)

    if N <= max_delay:
        raise ValueError("Not enough data points to estimate ARX model with these orders.")

    M = N - max_delay
    Phi = np.zeros((M, na + nb))
    Y = np.zeros(M)

    for t in range(max_delay, N):
        idx = t - max_delay
        Y[idx] = y[t]

        # Output history (negative signs for A polynomial)
        for i in range(1, na + 1):
            Phi[idx, i - 1] = -y[t - i]

        # Input history
        for j in range(1, nb + 1):
            Phi[idx, na + j - 1] = u[t - nk - j + 1]

    # Solve OLS: theta = (Phi^T Phi)^-1 Phi^T Y
    # Use pseudo-inverse for stability
    theta = np.linalg.pinv(Phi.T @ Phi) @ Phi.T @ Y

    return theta

def simulate_arx(u, theta, na, nb, nk):
    """
    Simulate the ARX model given input u and parameters theta.
    A(q) y(t) = B(q) u(t - nk) + e(t)
    """
    N = len(u)
    y_sim = np.zeros(N)

    a_params = theta[:na]
    b_params = theta[na:na+nb]

    max_delay = max(na, nb + nk - 1)

    for t in range(max_delay, N):
        y_val = 0

        # Output contribution
        for i in range(1, na + 1):
            y_val -= a_params[i-1] * y_sim[t - i]

        # Input contribution
        for j in range(1, nb + 1):
            y_val += b_params[j-1] * u[t - nk - j + 1]

        y_sim[t] = y_val

    return y_sim
