import os, shutil

for root, dirs, _ in os.walk(os.getcwd()):
    for _dir in dirs:
        _temp_dir = os.path.join(root, _dir)
        if _temp_dir.endswith('__pycache__'):
            shutil.rmtree(_temp_dir)