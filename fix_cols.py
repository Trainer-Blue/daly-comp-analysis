import json

with open('notebooks/03_model_lasso.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'drop_cols =' in ''.join(cell['source']):
        source_code = ''.join(cell['source'])
        new_source = source_code.replace("'event_idx', ", "").replace("'number', ", "")
        cell['source'] = new_source.splitlines(True)

with open('notebooks/03_model_lasso.ipynb', 'w') as f:
    json.dump(nb, f)
