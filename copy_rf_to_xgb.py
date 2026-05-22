import json

with open('notebooks/04_model_random_forest.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # Replacements
        source = source.replace('from sklearn.ensemble import RandomForestRegressor', 'from xgboost import XGBRegressor')
        source = source.replace('RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)', 'XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1)')
        source = source.replace('RandomForestRegressor', 'XGBRegressor')
        source = source.replace('Random Forest', 'XGBoost')
        source = source.replace('RF', 'XGBoost')
        
        # Reform string back to list of lines for JSON format
        lines = source.split('\n')
        cell['source'] = [line + '\n' for line in lines[:-1]]
        if len(lines) > 0:
            cell['source'].append(lines[-1])
            
        cell['outputs'] = []
        cell['execution_count'] = None

with open('notebooks/05_model_xgboost.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
