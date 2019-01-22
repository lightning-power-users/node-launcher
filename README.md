# User Guides

1. [Please start here!](https://medium.com/@pierre_rochard/windows-macos-lightning-network-284bd5034340)
2. [Set up Zap Desktop](https://medium.com/@pierre_rochard/easy-lightning-with-node-launcher-zap-488133edfbd)
3. [Open a channel with Zap Desktop](https://medium.com/@pierre_rochard/send-a-lightning-payment-with-zap-desktop-17b74b65b9b8)
4. [Send a payment with the Joule Chrome extension](https://medium.com/@pierre_rochard/bitcoin-lightning-joule-chrome-extension-ac149bb05cb9)

# Requirements
1. ~300 GB of download bandwidth
2. ~10 GB of disk space (~300 GB if you want the Bitcoin transaction index, makes for a faster LND)
3. Windows 7+ or macOS 10.12.6+

Please submit a pull request if you want to add Linux support! Next year is the Year of Desktop Linux...


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

0. `git clone https://github.com/PierreRochard/node-launcher && cd node-launcher`
1. Setup and activate Python 3.7.2 virtual environment
2. Install pipenv: `pip install pipenv`
3. Install packages from pipfile: `pipenv install --dev`
4. `python setup.py develop`
5. `python run.py`

# Managing packages with pipenv

Pipfile.lock takes advantage of security improvements in pip. By default, the Pipfile.lock will be generated with the sha256 hashes of each downloaded package. This will allow pip to guarantee you’re installing what you intend to when on a compromised network, or downloading dependencies from an untrusted PyPI endpoint.


`pip` itself should **not** be used directly to install or upgrade packages in this project's virtual environment packages to maintain compatibility

Installing packages:
* `pipenv install <package>`
or
* `pipenv install requests~=1.2   # equivalent to requests~=1.2.0`

Upgrading packages:
* Find out what’s changed upstream: `pipenv update --outdated`
* Upgrade everything: `pipenv update`
* Upgrade individual package: `pipenv update <pkg>`

After modifying installed packages:
* Generate a new Pipfile.lock: `pipenv lock`

Pipfile and Pipfile.lock should be included in VCS

# Testing

`pytest tests`

To include tests with network calls to GitHub:
`pytest tests --run_slow`


# Packaging

macOS: `pyinstaller run-mac.spec`

Windows: `pyinstaller run-windows.spec` (pyinstaller packaging only works on Windows 7)


# Generate LND Bindings

https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md