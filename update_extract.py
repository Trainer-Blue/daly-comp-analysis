import re

with open('src/extract_all.py', 'r') as f:
    content = f.read()

# Make sure we import extract_subjective_ratings
content = content.replace(
    "from eeg_utils import load_and_epoch_eeg, perform_ica, reject_artifacts",
    "from eeg_utils import load_and_epoch_eeg, perform_ica, reject_artifacts, extract_subjective_ratings"
)

# During the event loop, extract the TSV target ratings 
loop_code_old = """
                # Extract EEG ML Features
                eeg_feats = extract_eeg_features_from_epochs(clean_epochs)
                
                for f in eeg_feats:
"""

loop_code_new = """
                # Extract EEG ML Features
                eeg_feats = extract_eeg_features_from_epochs(clean_epochs)
                
                # Extract Target B Raw Ratings (with NaNs)
                events_df = pd.read_csv(tsv_path, sep='\\t')
                raw_ratings = extract_subjective_ratings(events_df)
                
                # Merge target B ratings into eeg_feats on track_id
                # (Since it's a single run, track_id is unique per epoch)
                eeg_feats_df = pd.DataFrame(eeg_feats)
                eeg_feats_df = pd.merge(eeg_feats_df, raw_ratings.drop(columns=['event_idx']), on='track_id', how='left')
                eeg_feats = eeg_feats_df.to_dict('records')
                
                for f in eeg_feats:
"""

content = content.replace(loop_code_old, loop_code_new)

with open('src/extract_all.py', 'w') as f:
    f.write(content)
