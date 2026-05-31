import pandas as pd, numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data/features/sub-01_features.csv') # just to get columns
aud_keywords = ['mfcc', 'chroma', 'zcr', 'spectral', 'rms', 'bpm', 'tempo']
aud_cols = [c for c in df.columns if any(k in c for k in aud_keywords)]
eeg_cols = [c for c in df.columns if c not in aud_cols and c.startswith('FP') or c.startswith('O') or c.startswith('P') or c.startswith('C') or c.startswith('F') or c.startswith('T')]
# Better approach: directly get from the notebook state

