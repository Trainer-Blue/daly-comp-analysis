import numpy as np
import scipy.signal

def calculate_hjorth_parameters(data):
    """
    Calculate Hjorth Mobility and Complexity for a given 1D array of EEG data.
    
    Parameters:
    data (ndarray): 1D continuous EEG signal
    
    Returns:
    tuple: (mobility, complexity)
    """
    # Calculate first and second derivatives
    dx = np.diff(data)
    ddx = np.diff(dx)
    
    # Calculate variances
    var_x = np.var(data)
    var_dx = np.var(dx)
    var_ddx = np.var(ddx)
    
    # Calculate Mobility and Complexity
    if var_x == 0 or var_dx == 0:
        return 0, 0
        
    mobility = np.sqrt(var_dx / var_x)
    mobility_dx = np.sqrt(var_ddx / var_dx)
    complexity = mobility_dx / mobility
    
    return mobility, complexity

def calculate_band_powers(data, sfreq=500.0):
    """
    Calculate absolute band powers for Delta, Theta, Alpha, Beta, Gamma bands.
    Using Welch's method.
    """
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 80)
    }
    
    freqs, psd = scipy.signal.welch(data, sfreq, nperseg=int(sfreq*2))
    
    band_powers = {}
    for band_name, (fmin, fmax) in bands.items():
        idx = np.logical_and(freqs >= fmin, freqs <= fmax)
        band_power = scipy.integrate.simps(psd[idx], freqs[idx])
        band_powers[band_name] = band_power
        
    return band_powers

def extract_eeg_features_from_epochs(epochs):
    """
    Iterate over epochs and channels to extract Hjorth parameters and band powers.
    Returns a dictionary mapping epoch events (event_id/track_id) to their features.
    """
    data = epochs.get_data() # Shape: (n_epochs, n_channels, n_times)
    ch_names = epochs.ch_names
    event_ids = epochs.events[:, 2] # the 301-360 codes
    sfreq = epochs.info['sfreq']
    
    features_list = []
    
    for i in range(len(event_ids)):
        epoch_data = data[i]
        event_code = event_ids[i]
        track_id = event_code - 300 # Convert to actual track number
        
        feature_dict = {'track_id': track_id}
        
        for ch_idx, ch_name in enumerate(ch_names):
            channel_signal = epoch_data[ch_idx]
            
            # Hjorth
            mobility, complexity = calculate_hjorth_parameters(channel_signal)
            feature_dict[f'{ch_name}_hjorth_mobility'] = mobility
            feature_dict[f'{ch_name}_hjorth_complexity'] = complexity
            
            # Band powers
            bp = calculate_band_powers(channel_signal, sfreq)
            for band, power in bp.items():
                feature_dict[f'{ch_name}_{band}_power'] = power
                
        features_list.append(feature_dict)
        
    return features_list
