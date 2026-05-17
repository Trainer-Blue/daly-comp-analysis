import mne
import pandas as pd
import numpy as np
import os

def load_and_epoch_eeg(edf_path, events_tsv_path, tmin=0.0, tmax=15.0):
    """
    Loads an EDF file and its corresponding events TSV, filters for music 
    stimuli events (301-360), and returns the 15-second epochs.
    """
    # Load raw EEG data
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose='ERROR')
    
    # Standardize montage (e.g. standard 10-20 system)
    # The dataset uses a standard 19-channel acticap/brainamp setup usually, 
    # but let's just make sure channel types are set as 'eeg'.
    raw.set_channel_types({ch: 'eeg' for ch in raw.ch_names if ch != 'STI 014'})
    
    # Read the TSV events file
    events_df = pd.read_csv(events_tsv_path, sep='\t')
    
    # Filter for stimuli events (values 301 to 360 represent the music clips)
    music_events_df = events_df[(events_df['value'] >= 301) & (events_df['value'] <= 360)]
    
    # MNE expects events in a specific 3-column numpy array format:
    # [sample_number, 0, event_id]
    sfreq = raw.info['sfreq']
    
    # Convert onset times to sample numbers
    sample_numbers = (music_events_df['onset'] * sfreq).astype(int).values
    event_ids = music_events_df['value'].astype(int).values
    zeros = np.zeros_like(sample_numbers)
    
    mne_events = np.column_stack([sample_numbers, zeros, event_ids])
    
    # Create Epochs (from tmin to tmax)
    epochs = mne.Epochs(
        raw, 
        events=mne_events, 
        event_id=None, # Keep all found event IDs
        tmin=tmin, 
        tmax=tmax,
        baseline=(0, 0), # Baseline correct to the very start of the clip
        preload=True,
        verbose='ERROR'
    )
    
    return epochs

def reject_artifacts(epochs, threshold_uv=100):
    """
    Rejects epochs where the peak-to-peak amplitude exceeds the given threshold.
    Daly et al. (2015) dropped trials with > ±100 µV amplitude.
    mne.Epochs.drop_bad uses peak-to-peak (max - min) in Volts, 
    so 100 µV -> peak-to-peak of 200 µV to be safe, but let's strictly use 
    threshold_uv for the peak-to-peak rejection directly (often 100e-6 V).
    """
    # Convert threshold from microvolts to volts
    reject_criteria = dict(eeg=threshold_uv * 1e-6)
    
    # Drop bad epochs based on amplitude
    epochs.drop_bad(reject=reject_criteria, verbose='INFO')
    
    return epochs
