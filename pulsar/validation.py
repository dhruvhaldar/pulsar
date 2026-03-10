import numpy as np
from scipy.signal import correlate

def auto_correlation(e, max_lag):
    """
    Calculate auto-correlation of residuals phi_ee(tau)
    e: residuals (y - y_hat)
    """
    N = len(e)
    # Mean center
    e = e - np.mean(e)

    # Calculate auto-correlation
    r = correlate(e, e, mode='full')
    lags = np.arange(-N + 1, N)

    # Extract only positive lags up to max_lag
    center = N - 1
    r_pos = r[center:center + max_lag + 1]

    # Normalize
    if r_pos[0] != 0:
        r_pos = r_pos / r_pos[0]

    return r_pos

def cross_correlation(u, e, max_lag):
    """
    Calculate cross-correlation between inputs and residuals phi_ue(tau)
    u: input
    e: residuals
    """
    N = len(e)
    # Mean center
    u = u - np.mean(u)
    e = e - np.mean(e)

    # Calculate cross-correlation
    r = correlate(e, u, mode='full')
    lags = np.arange(-N + 1, N)

    # Extract lags from -max_lag to max_lag
    center = N - 1
    start = max(0, center - max_lag)
    end = min(2 * N - 1, center + max_lag + 1)

    r_extract = r[start:end]

    # Normalize by std deviations
    std_u = np.std(u)
    std_e = np.std(e)

    if std_u != 0 and std_e != 0:
        r_extract = r_extract / (N * std_u * std_e)

    return r_extract
