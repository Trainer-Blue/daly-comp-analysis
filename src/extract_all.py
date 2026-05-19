import os
import sys
import argparse
import pandas as pd
from tqdm import tqdm
import warnings

# Suppress verbose warnings from MNE during batch processing
warnings.filterwarnings('ignore')

from eeg_utils import load_and_epoch_eeg, perform_ica, reject_artifacts
from features import extract_eeg_features_from_epochs
from audio_utils import batch_extract_audio_features

def main():
    parser = argparse.ArgumentParser(description='Batch extract EEG and Audio ML Features')
    parser.add_argument('--start-sub', type=int, default=1, help='Starting subject number (1-31)')
    parser.add_argument('--end-sub', type=int, default=31, help='Ending subject number (1-31)')
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data')
    out_dir = os.path.join(data_dir, 'features')
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load targets
    print("Loading target ratings...")
    ratings_path = os.path.join(data_dir, 'music', 'mean_ratings_set1.csv')
    ratings_df = pd.read_csv(ratings_path)
    ratings_df.rename(columns={'number': 'track_id'}, inplace=True)
    
    # 2. Extract / Load all Audio Features
    print("Extracting Audio features for all 360 tracks...")
    audio_dir = os.path.join(data_dir, 'music', 'Set1', 'Set1')
    audio_features_list = batch_extract_audio_features(audio_dir)
    audio_df = pd.DataFrame(audio_features_list)
    
    # Merge audio features with targets
    track_info_df = pd.merge(audio_df, ratings_df, on='track_id', how='inner')
    print(f"Loaded Track Info Shape: {track_info_df.shape}")
    
    # 3. Iterate through subjects
    for sub_id in range(args.start_sub, args.end_sub + 1):
        subj_str = f"sub-{sub_id:02d}"
        print(f"\n======================================")
        print(f"Processing {subj_str}...")
        print(f"======================================")
        
        subj_features = []
        
        # Iterate through runs (1 to 6)
        # Note: 1 and 6 might be resting state but we try to load them anyway. 
        # If there are no music events, the epoching will just be empty.
        for run_id in range(1, 7):
            edf_path = os.path.join(data_dir, subj_str, 'eeg', f'{subj_str}_task-run{run_id}_eeg.edf')
            tsv_path = os.path.join(data_dir, subj_str, 'eeg', f'{subj_str}_task-run{run_id}_events.tsv')
            
            if not os.path.exists(edf_path) or not os.path.exists(tsv_path):
                print(f"  [{subj_str} Run {run_id}] Missing files, skipping.")
                continue
                
            try:
                # Load and epoch
                epochs = load_and_epoch_eeg(edf_path, tsv_path)
                if len(epochs) == 0:
                    continue
                    
                # Clean
                ica_epochs = perform_ica(epochs)
                clean_epochs = reject_artifacts(ica_epochs, threshold_uv=300)
                
                if len(clean_epochs) == 0:
                    print(f"  [{subj_str} Run {run_id}] All epochs dropped due to artifacts.")
                    continue
                
                # Extract EEG ML Features
                eeg_feats = extract_eeg_features_from_epochs(clean_epochs)
                
                for f in eeg_feats:
                    # also record which run we used
                    f['run'] = run_id
                    f['subject'] = subj_str
                
                subj_features.extend(eeg_feats)
                print(f"  [{subj_str} Run {run_id}] Successfully extracted {len(eeg_feats)} epochs.")
                
            except Exception as e:
                print(f"  [{subj_str} Run {run_id}] Error processing: {str(e)}")
                
        # 4. Save to CSV for the subject
        if len(subj_features) > 0:
            subj_eeg_df = pd.DataFrame(subj_features)
            # Merge with audio+targets
            final_subj_df = pd.merge(subj_eeg_df, track_info_df, on='track_id', how='inner')
            out_file = os.path.join(out_dir, f"{subj_str}_features.csv")
            final_subj_df.to_csv(out_file, index=False)
            print(f"-> Saved {len(final_subj_df)} valid trials for {subj_str} to {out_file}")
            
            # Memory cleanup
            del subj_eeg_df
            del final_subj_df
        else:
            print(f"-> NO valid data recovered for {subj_str}.")

if __name__ == '__main__':
    main()
