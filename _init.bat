pip install virtualenv
python -m virtualenv --python="P:\x64\py312\python.exe" env
cmd /U /k "env\Scripts\activate&&pip install -r requirements.txt&&exit"
cmd /U /k "env\Scripts\activate"