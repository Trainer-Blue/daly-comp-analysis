import mne
import pandas as pd
import numpy as np
import os

def load_and_epoch_eeg(edf_path, events_tsv_path, tmin=0.0, tmax=15.0):
    """
    Loads an EDF file and its corresponding events TSV, filters for music 
    stimuli events (301-660), and returns the 15-second epochs.
    """
    # Load raw EEG data
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose='ERROR')
    
    # Standardize montage (e.g. standard 10-20 system)
    # The dataset uses a standard 19-channel acticap/brainamp setup usually, 
    # but let's just make sure channel types are set as 'eeg'.
    raw.set_channel_types({ch: 'eeg' for ch in raw.ch_names if ch != 'STI 014'})
    
    # Apply standard EEG bandpass filter (0.5 Hz to 45 Hz) to remove DC drift and high-freq noise
    raw.filter(l_freq=0.5, h_freq=45.0, verbose='ERROR')
    
    # Read the TSV events file
    events_df = pd.read_csv(events_tsv_path, sep='\t')
    
    # Filter for stimuli events (values 301 to 660 represent the music clips)
    music_events_df = events_df[(events_df['trial_type'] >= 301) & (events_df['trial_type'] <= 660)]
    
    # MNE expects events in a specific 3-column numpy array format:
    # [sample_number, 0, event_id]
    sfreq = raw.info['sfreq']
    
    # Convert onset times to sample numbers
    sample_numbers = (music_events_df['onset'] * sfreq).astype(int).values
    event_ids = music_events_df['trial_type'].astype(int).values
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

def perform_ica(epochs, random_state=42):
    """
    Fits an Independent Component Analysis (ICA) on the epochs, attempts to automatically
    detect eye-blink components using FP1 as a proxy EOG, and subtracts them.
    This mimics the standard Daly/Krish preprocessing workflow before amplitude rejection.
    """
    # Fit ICA using FastICA algorithm
    ica = mne.preprocessing.ICA(n_components=15, random_state=random_state, method='fastica')
    ica.fit(epochs, verbose='ERROR')
    
    # Try to find eye blink components using FP1 as surrogate EOG
    if 'FP1' in epochs.ch_names:
        eog_indices, eog_scores = ica.find_bads_eog(epochs, ch_name='FP1', verbose='ERROR')
        ica.exclude = eog_indices
    
    # Apply the ICA to a copy of the epochs (leaves original untouched)
    clean_epochs = ica.apply(epochs.copy(), verbose='ERROR')
    return clean_epochs

def reject_artifacts(epochs, threshold_uv=200):
    """
    Rejects epochs where the peak-to-peak amplitude exceeds the given threshold.
    Daly et al. (2015) dropped trials with > ±100 µV amplitude.
    mne.Epochs.drop_bad uses peak-to-peak (max - min) in Volts.
    A scalar amplitude of ±100 µV corresponds to a peak-to-peak threshold of 200 µV.
    """
    # Convert threshold from microvolts to volts
    reject_criteria = dict(eeg=threshold_uv * 1e-6)
    
    # Drop bad epochs based on amplitude
    epochs.drop_bad(reject=reject_criteria, verbose='INFO')
    
    return epochs

def extract_subjective_ratings(events_df):
    """
    Scans the events dataframe for music events (301-660) and 
    extracts the subjective ratings from the subsequent questions (800-807).
    Answers are coded as 901-909 (1 to 9 Likert scale).
    If a question is missing or not answered, it is left as np.nan.
    
    Returns:
        pd.DataFrame: A dataframe containing 'track_id' and rating columns Q800 to Q807.
    """
    ratings_list = []
    
    music_indices = events_df.index[(events_df['trial_type'] >= 301) & (events_df['trial_type'] <= 660)].tolist()
    
    for i, music_idx in enumerate(music_indices):
        track_id = int(events_df.loc[music_idx, 'trial_type']) - 300
        
        start_idx = music_idx + 1
        end_idx = music_indices[i+1] if i + 1 < len(music_indices) else len(events_df)
        
        window = events_df.iloc[start_idx:end_idx]
        
        ans_dict = {f'Q{q}': np.nan for q in range(800, 808)}
        ans_dict['event_idx'] = music_idx
        ans_dict['track_id'] = track_id
        
        q_indices = window.index[(window['trial_type'] >= 800) & (window['trial_type'] <= 807)].tolist()
        
        for q_idx in q_indices:
            q_code = int(events_df.loc[q_idx, 'trial_type'])
            ans_search_window = events_df.iloc[q_idx : min(q_idx + 3, len(events_df))]
            ans_event = ans_search_window[(ans_search_window['trial_type'] >= 901) & (ans_search_window['trial_type'] <= 909)]
            
            if not ans_event.empty:
                ans_code = int(ans_event.iloc[0]['trial_type'])
                rating = ans_code - 900
                # only keep first answer to avoid overwriting with subsequent accidental presses
                if np.isnan(ans_dict[f'Q{q_code}']):
                    ans_dict[f'Q{q_code}'] = rating
                
        ratings_list.append(ans_dict)
        
    return pd.DataFrame(ratings_list)
