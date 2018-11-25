# Requirements
1. Bitcoin Core https://bitcoincore.org/en/download/
2. ~300 GB of download bandwidth
3. ~7 GB of disk space
4. Python 3.7

# Node Launcher

1. Creates a node launcher data directory 
    * macOS: `~/Library/Application Support/Node Launcher/`
    * Windows: `%localappdata%/Node\ Launcher/`
    * Linux: `~/.node_launcher`
2. Finds available ports for Bitcoin and LND, testnet and mainnet
3. When launched, nodes use the node launcher data directory, not the default data directories
4. Nodes are pruned by default and take up to 8 GB of disk space
5. Pruning still requires downloading data, so make sure you can handle downloading ~300 GB of data


# Development

0. `git clone https://github.com/PierreRochard/node-launcher && cd node-launcher`
1. Setup a Python 3.7+ virtual environment
2. `python -m pip install --index-url=http://download.qt.io/snapshots/ci/pyside/5.11/latest pyside2 --trusted-host download.qt.io`
3. `pip install -r requirements.txt`
4. `python setup.py develop`
5. `python run.py`

# Testing

`pytest tests`

To include tests with network calls to GitHub:
`pytest tests --run_slow`


# Packaging

macOS: `pyinstaller run-mac.spec`

Windows: `pyinstaller run-windows.spec` (only works on Windows 7)