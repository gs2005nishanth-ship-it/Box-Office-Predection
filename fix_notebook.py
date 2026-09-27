import json
import os

notebook_path = "box-office-prediction.ipynb"
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Replace hardcoded Windows paths with local filenames
for cell in nb["cells"]:
    if cell.get("cell_type") == "code":
        new_source = []
        for line in cell.get("source", []):
            line = line.replace(r'C:\Users\Ritdhvika\Downloads\train.csv', 'train.csv')
            line = line.replace(r'C:\Users\Rithvika\Downloads\train.csv', 'train.csv')
            line = line.replace(r'C:\Users\Ritdhvika\Downloads\test.csv', 'test.csv')
            line = line.replace(r'C:\Users\Rithvika\Downloads\test.csv', 'test.csv')
            line = line.replace(r'C:\Users\Ritdhvika\Downloads\sample_submission.csv', 'sample_submission.csv')
            line = line.replace(r'C:\Users\Rithvika\Downloads\sample_submission.csv', 'sample_submission.csv')
            # Fix chained assignment indexing warnings
            line = line.replace("train['runtime'][2302]=86", "train.loc[train.index == 2302, 'runtime'] = 86")
            line = line.replace("train['runtime'][1335]=130", "train.loc[train.index == 1335, 'runtime'] = 130")
            line = line.replace("test['runtime'][243] = 93", "test.loc[test.index == 243, 'runtime'] = 93")
            line = line.replace("test['runtime'][1489] = 91", "test.loc[test.index == 1489, 'runtime'] = 91")
            line = line.replace("test['runtime'][1632] = 100", "test.loc[test.index == 1632, 'runtime'] = 100")
            line = line.replace("test['runtime'][3817] = 90", "test.loc[test.index == 3817, 'runtime'] = 90")
            # Fix scikit-learn mean_squared_error squared parameter
            line = line.replace("squared=False", "")
            new_source.append(line)
        cell["source"] = new_source

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Notebook paths and syntax successfully updated!")
