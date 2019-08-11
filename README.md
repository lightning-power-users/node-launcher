# User Guides

1. [Please start here!](https://medium.com/@pierre_rochard/windows-macos-lightning-network-284bd5034340)
2. [Send a payment with the Joule Chrome extension](https://medium.com/@pierre_rochard/bitcoin-lightning-joule-chrome-extension-ac149bb05cb9)

# Requirements
1. ~300 GB of download bandwidth
2. ~10 GB of disk space (~300 GB if you want the Bitcoin transaction index, makes for a faster LND)
3. Windows 7+ or macOS 10.12.6+

Linux works but it is not packaged, follow the developer steps below to run it from the Linux command line. 

Please submit a pull request if you want to add Linux packaging! A .deb and .rpm would help grow the Lightning network...


# Install 

Download and open the latest release for your operating system: 
https://github.com/PierreRochard/node-launcher/releases

# Node Launcher

1. Creates a node launcher data directory 
    * macOS: `~/Library/Application Support/Node Launcher/`
    * Windows: `%localappdata%/Node\ Launcher/`
2. Finds available ports for Bitcoin and LND, testnet and mainnet
3. When launched, Bitcoin nodes use the `datadir` directory specified in `bitcoin.conf` (or the default data directory)
4. If you don't have >300 GB of disk space free, Bitcoin nodes will fall back to pruned
5. Pruning still requires downloading data, so make sure you can handle downloading ~300 GB of data

![macos](https://raw.githubusercontent.com/PierreRochard/node-launcher/master/macos.png)

![windows](https://raw.githubusercontent.com/PierreRochard/node-launcher/master/windows.png)

# Development

Review the contributing.md file https://github.com/PierreRochard/node-launcher/blob/master/contributing.md

Install Python3.7+

macOS: `brew install python3 dbus dbus-glib`

Linux: `sudo apt install python3.7-venv libdbus-glib-1-dev python3.7-dev`

For Windows see https://medium.com/@pierre_rochard/node-launcher-developer-setup-on-windows-5ba6e0fbb38a

For macOS and Linux:

0. `git clone https://github.com/PierreRochard/node-launcher`
1. `cd node-launcher`
2. `python3.7 -m venv venv`
3. `. venv/bin/activate`
4. `pip3.7 install -r requirements.txt`
5. `python setup.py develop`
6. `python run.py`

# Testing

`pytest tests`

To include tests with network calls to GitHub:
`pytest tests --run_slow`


# Packaging

macOS: `pyinstaller run-mac.spec`

Windows: `pyinstaller run-windows.spec` (pyinstaller packaging only works on Windows 7)


# Generate LND Bindings

https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md
