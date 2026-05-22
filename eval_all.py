import os
import glob
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

base_path = os.path.abspath(os.getcwd())
features_dir = os.path.join(base_path, 'data', 'features')
csv_files = glob.glob(os.path.join(features_dir, 'sub-*_features.csv'))
full_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

q_cols = [f'Q{q}' for q in range(800, 808)]
imputer = KNNImputer(n_neighbors=5, weights='distance')
imputed_ratings = imputer.fit_transform(full_df[q_cols])

pca = PCA(n_components=3)
target_b_pca = pca.fit_transform(imputed_ratings)

full_df['PC1_Valence_Subj'] = target_b_pca[:, 0]
full_df['PC2_Energy_Subj'] = target_b_pca[:, 1]
full_df['PC3_Tension_Subj'] = target_b_pca[:, 2]

drop_cols = ['track_id', 'run', 'subject'] + q_cols + \
            ['number', 'valence', 'energy', 'tension', 'anger', 'fear', 'happy', 'sad', 'tender', 'TARGET'] + \
            ['PC1_Valence_Subj', 'PC2_Energy_Subj', 'PC3_Tension_Subj']
drop_cols = [c for c in drop_cols if c in full_df.columns]
X = full_df.drop(columns=drop_cols)
subjects = full_df['subject'].unique()

models = {
    'Lasso': Lasso(alpha=0.1, random_state=42, max_iter=10000),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1)
}
targets = ['PC1_Valence_Subj', 'PC2_Energy_Subj', 'PC3_Tension_Subj']

results_table = []

for pc in targets:
    row = {'Response PCs': pc}
    for model_name, model in models.items():
        actuals = []
        predictions = []
        for test_sub in subjects:
            train_idx = full_df['subject'] != test_sub
            test_idx = full_df['subject'] == test_sub
            
            X_train, y_train = X[train_idx], full_df.loc[train_idx, pc]
            X_test, y_test = X[test_idx], full_df.loc[test_idx, pc]
            
            if model_name == 'Lasso':
                scaler = StandardScaler()
                X_train_final = scaler.fit_transform(X_train)
                X_test_final = scaler.transform(X_test)
            else:
                X_train_final, X_test_final = X_train.values, X_test.values
            
            model.fit(X_train_final, y_train)
            preds = model.predict(X_test_final)
            predictions.extend(preds)
            actuals.extend(y_test)
        
        corr = np.corrcoef(actuals, predictions)[0,1]
        row[model_name] = f"{corr:.4f}"
    
    results_table.append(row)

df_results = pd.DataFrame(results_table)
print(df_results.to_markdown(index=False))
