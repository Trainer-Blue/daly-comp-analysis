import os
import glob
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr

def load_all_features(features_dir):
    """Load and concatenate all subject feature CSVs into a single DataFrame."""
    all_files = glob.glob(os.path.join(features_dir, '*_features.csv'))
    df_list = [pd.read_csv(f) for f in all_files]
    if len(df_list) == 0:
        raise ValueError("No feature CSVs found.")
    master_df = pd.concat(df_list, ignore_index=True)
    return master_df

def loso_cv(df, model, target_col):
    """
    Perform Leave-One-Subject-Out Cross Validation.
    """
    subjects = df['subject'].unique()
    print(f"Total unique subjects for LOSO: {len(subjects)}")
    
    meta_cols = ['track_id', 'run', 'subject', 'TARGET', 
                 'valence', 'energy', 'tension', 
                 'anger', 'fear', 'happy', 'sad', 'tender']
                 
    feature_cols = [c for c in df.columns if c not in meta_cols]
    
    rmses, r2s, pearsons = [], [], []
    
    for test_sub in subjects:
        train_df = df[df['subject'] != test_sub]
        test_df = df[df['subject'] == test_sub]
        
        X_train = train_df[feature_cols].values
        y_train = train_df[target_col].values
        
        X_test = test_df[feature_cols].values
        y_test = test_df[target_col].values
        
        # Scale features using training data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Predict
        preds = model.predict(X_test_scaled)
        
        # Calculate Metrics
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        if np.std(preds) == 0 or np.std(y_test) == 0:
            pearson = 0.0
        else:
            pearson, _ = pearsonr(y_test, preds)
            
        rmses.append(rmse)
        r2s.append(r2)
        pearsons.append(pearson)
        
    return {
        'target': target_col,
        'rmse_mean': np.mean(rmses),
        'rmse_std': np.std(rmses),
        'r2_mean': np.mean(r2s),
        'r2_std': np.std(r2s),
        'pearson_mean': np.mean(pearsons),
        'pearson_std': np.std(pearsons)
    }
