import json

with open('notebooks/03_model_lasso.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        if 'outputs' not in cell:
            cell['outputs'] = []

with open('notebooks/03_model_lasso.ipynb', 'w') as f:
    json.dump(nb, f)
