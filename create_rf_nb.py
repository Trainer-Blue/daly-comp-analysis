import json
import os

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Notebook 04: Random Forest Model with Leave-One-Subject-Out (LOSO) Cross-Validation\n",
            "\n",
            "Here we evaluate a non-linear ensemble strategy (Random Forest) to see if it overcomes the linear limitations of the Lasso baseline. This model leverages bagged decision trees which naturally ignore extreme outliers and capture non-linear relationships."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "import os\n",
            "import glob\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "from sklearn.impute import KNNImputer\n",
            "from sklearn.decomposition import PCA\n",
            "from sklearn.ensemble import RandomForestRegressor\n",
            "from sklearn.metrics import mean_squared_error, r2_score\n",
            "from tqdm import tqdm\n",
            "\n",
            "base_path = os.path.abspath(os.path.join(os.getcwd(), '..'))\n",
            "features_dir = os.path.join(base_path, 'data', 'features')\n",
            "\n",
            "csv_files = glob.glob(os.path.join(features_dir, 'sub-*_features.csv'))\n",
            "df_list = []\n",
            "for f in csv_files:\n",
            "    df_list.append(pd.read_csv(f))\n",
            "\n",
            "full_df = pd.concat(df_list, ignore_index=True)\n",
            "print(f\"Total trials collected: {len(full_df)}\")\n"
        ],
        "outputs": []
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "# Subjective Rating Columns\n",
            "q_cols = [f'Q{q}' for q in range(800, 808)]\n",
            "\n",
            "# Impute missing Likert scale inputs across all subjects\n",
            "imputer = KNNImputer(n_neighbors=5, weights='distance')\n",
            "imputed_ratings = imputer.fit_transform(full_df[q_cols])\n",
            "\n",
            "# Apply PCA\n",
            "pca = PCA(n_components=3)\n",
            "target_b_pca = pca.fit_transform(imputed_ratings)\n",
            "\n",
            "full_df['PC1_Valence_Subj'] = target_b_pca[:, 0]\n",
            "full_df['PC2_Energy_Subj'] = target_b_pca[:, 1]\n",
            "full_df['PC3_Tension_Subj'] = target_b_pca[:, 2]\n",
            "print(f\"Explained Variance by 3 PCs: {sum(pca.explained_variance_ratio_):.2f}\")\n"
        ],
        "outputs": []
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "drop_cols = ['track_id', 'run', 'subject'] + q_cols + \\\n",
            "            ['number', 'valence', 'energy', 'tension', 'anger', 'fear', 'happy', 'sad', 'tender', 'TARGET'] + \\\n",
            "            ['PC1_Valence_Subj', 'PC2_Energy_Subj', 'PC3_Tension_Subj']\n",
            "\n",
            "# Drop columns to isolate pure EEG + Audio features (ignore KeyErrors if already dropped)\n",
            "drop_cols = [c for c in drop_cols if c in full_df.columns]\n",
            "X = full_df.drop(columns=drop_cols)\n",
            "print(f\"Feature matrix shape (X): {X.shape}\")\n"
        ],
        "outputs": []
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "subjects = full_df['subject'].unique()\n",
            "predictions = []\n",
            "actuals = []\n",
            "\n",
            "for test_sub in tqdm(subjects, desc=\"LOSO Fold\"):\n",
            "    train_idx = full_df['subject'] != test_sub\n",
            "    test_idx = full_df['subject'] == test_sub\n",
            "    \n",
            "    X_train, y_train = X[train_idx], full_df.loc[train_idx, 'PC1_Valence_Subj']\n",
            "    X_test, y_test = X[test_idx], full_df.loc[test_idx, 'PC1_Valence_Subj']\n",
            "    \n",
            "    # Fit Random Forest (Scaling is generally not strictly required for decision tree ensembles)\n",
            "    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)\n",
            "    model.fit(X_train, y_train)\n",
            "    \n",
            "    # Predict\n",
            "    preds = model.predict(X_test)\n",
            "    \n",
            "    predictions.extend(preds)\n",
            "    actuals.extend(y_test.values)\n",
            "\n",
            "rmse = np.sqrt(mean_squared_error(actuals, predictions))\n",
            "r2 = r2_score(actuals, predictions)\n",
            "correlation = np.corrcoef(actuals, predictions)[0, 1]\n",
            "\n",
            "print(f\"\\n--- LOSO Validation Results RF (PC1: Valence) ---\")\n",
            "print(f\"RMSE: {rmse:.4f}\")\n",
            "print(f\"R² Score: {r2:.4f}\")\n",
            "print(f\"Pearson Correlation (r): {correlation:.4f}\")\n"
        ],
        "outputs": []
    }
]

nb = {
    "cells": cells,
    "metadata": {
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open('notebooks/04_model_random_forest.ipynb', 'w') as f:
    json.dump(nb, f)
