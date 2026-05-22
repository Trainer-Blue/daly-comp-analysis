#!/usr/bin/env python
# coding: utf-8

# # Notebook 04: Random Forest Model with Leave-One-Subject-Out (LOSO) Cross-Validation
# 
# Here we evaluate a non-linear ensemble strategy (Random Forest) to see if it overcomes the linear limitations of the Lasso baseline. This model leverages bagged decision trees which naturally ignore extreme outliers and capture non-linear relationships.

# In[1]:


import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from tqdm import tqdm

base_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
features_dir = os.path.join(base_path, 'data', 'features')

csv_files = glob.glob(os.path.join(features_dir, 'sub-*_features.csv'))
df_list = []
for f in csv_files:
    df_list.append(pd.read_csv(f))

full_df = pd.concat(df_list, ignore_index=True)
print(f"Total trials collected: {len(full_df)}")


# In[2]:


# Subjective Rating Columns
q_cols = [f'Q{q}' for q in range(800, 808)]

# Impute missing Likert scale inputs across all subjects
imputer = KNNImputer(n_neighbors=5, weights='distance')
imputed_ratings = imputer.fit_transform(full_df[q_cols])

# Apply PCA
pca = PCA(n_components=3)
target_b_pca = pca.fit_transform(imputed_ratings)

full_df['PC1_Valence_Subj'] = target_b_pca[:, 0]
full_df['PC2_Energy_Subj'] = target_b_pca[:, 1]
full_df['PC3_Tension_Subj'] = target_b_pca[:, 2]
print(f"Explained Variance by 3 PCs: {sum(pca.explained_variance_ratio_):.2f}")


# In[3]:


drop_cols = ['track_id', 'run', 'subject'] + q_cols + \
            ['number', 'valence', 'energy', 'tension', 'anger', 'fear', 'happy', 'sad', 'tender', 'TARGET'] + \
            ['PC1_Valence_Subj', 'PC2_Energy_Subj', 'PC3_Tension_Subj']

# Drop columns to isolate pure EEG + Audio features (ignore KeyErrors if already dropped)
drop_cols = [c for c in drop_cols if c in full_df.columns]
X = full_df.drop(columns=drop_cols)
print(f"Feature matrix shape (X): {X.shape}")


# In[4]:


subjects = full_df['subject'].unique()
predictions = []
actuals = []

for test_sub in tqdm(subjects, desc="LOSO Fold"):
    train_idx = full_df['subject'] != test_sub
    test_idx = full_df['subject'] == test_sub

    X_train, y_train = X[train_idx], full_df.loc[train_idx, 'PC1_Valence_Subj']
    X_test, y_test = X[test_idx], full_df.loc[test_idx, 'PC1_Valence_Subj']

    # Fit Random Forest (Scaling is generally not strictly required for decision tree ensembles)
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Predict
    preds = model.predict(X_test)

    predictions.extend(preds)
    actuals.extend(y_test.values)

rmse = np.sqrt(mean_squared_error(actuals, predictions))
r2 = r2_score(actuals, predictions)
correlation = np.corrcoef(actuals, predictions)[0, 1]

print(f"\n--- LOSO Validation Results RF (PC1: Valence) ---")
print(f"RMSE: {rmse:.4f}")
print(f"R² Score: {r2:.4f}")
print(f"Pearson Correlation (r): {correlation:.4f}")

