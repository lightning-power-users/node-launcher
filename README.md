# Development

0. `git clone https://github.com/PierreRochard/node-launcher && cd node-launcher`
1. Setup a Python 3.6+ virtual environment
2. `python -m pip install --index-url=http://download.qt.io/snapshots/ci/pyside/5.11/latest pyside2 --trusted-host download.qt.io`
3. `pip install -r requirements.txt`
4. `python setup.py develop`
5. `python run.py`

# Testing

`pytest tests`

To include tests with network calls to GitHub:
`pytest tests --run_slow`


# Packaging

macOS:

`pyinstaller --windowed --onefile  run.spec`