from node_launcher.constants import LND, TOR, BITCOIND, WINDOWS, LINUX, DARWIN

TARGET_TOR_RELEASE = '9.0.7'
TARGET_WINDOWS_TOR_VERSION = '0.4.2.6'

TARGET_BITCOIN_RELEASE = 'v0.19.1'
TARGET_LND_RELEASE = 'v0.9.2-beta'

SOFTWARE_METADATA = {
    TOR: {
        'release_url': f'http://www.torproject.org/dist/torbrowser/{TARGET_TOR_RELEASE}',
        'cli_name': None
    },
    BITCOIND: {
        'release_url': f'https://bitcoincore.org/bin/bitcoin-core-{TARGET_BITCOIN_RELEASE.replace("v", "")}',
        'cli_name': 'bitcoin-cli'
    },
    LND: {
        'release_url': f'https://github.com/lightningnetwork/lnd/releases/download/{TARGET_LND_RELEASE}',
        'cli_name': 'lncli'
    }
}

OS_SOFTWARE_METADATA = {
    TOR: {
        WINDOWS: {
            'compressed_suffix': '.zip',
            'download_name': 'tor-win64-{release_version}',
            'release_version': TARGET_WINDOWS_TOR_VERSION,
            'daemon_name': 'tor'
        },
        LINUX: {
            'compressed_suffix': '.tar.xz',
            'download_name': 'tor-browser-linux64-{release_version}_en-US',
            'release_version': TARGET_TOR_RELEASE,
            'daemon_name': 'tor'
        },
        DARWIN: {
            'compressed_suffix': '.dmg',
            'download_name': 'TorBrowser-{release_version}-osx64_en-US',
            'release_version': TARGET_TOR_RELEASE,
            'daemon_name': 'tor.real'
        }
    },
    BITCOIND: {
        WINDOWS: {
            'compressed_suffix': '.zip',
            'download_name': f'bitcoin-{TARGET_BITCOIN_RELEASE.replace("v", "")}-win64',
            'release_version': TARGET_BITCOIN_RELEASE.replace('v', ''),
            'daemon_name': 'bitcoind'
        },
        LINUX: {
            'compressed_suffix': '.tar.xz',
            'download_name': f'bitcoin-{TARGET_BITCOIN_RELEASE.replace("v", "")}-x86_64-linux-gnu',
            'release_version': TARGET_BITCOIN_RELEASE.replace('v', ''),
            'daemon_name': 'bitcoind'
        },
        DARWIN: {
            'compressed_suffix': '.tar.gz',
            'download_name': f'bitcoin-{TARGET_BITCOIN_RELEASE.replace("v", "")}-osx64',
            'release_version': TARGET_BITCOIN_RELEASE.replace('v', ''),
            'daemon_name': 'bitcoind'
        }

    },
    LND: {
        WINDOWS: {
            'compressed_suffix': '.zip',
            'download_name': f'lnd-windows-amd64-{TARGET_LND_RELEASE}',
            'release_version': TARGET_LND_RELEASE,
            'daemon_name': 'lnd'
        },
        LINUX: {
            'compressed_suffix': '.tar.gz',
            'download_name': f'lnd-linux-amd64-{TARGET_LND_RELEASE}',
            'release_version': TARGET_LND_RELEASE,
            'daemon_name': 'lnd'
        },
        DARWIN: {
            'compressed_suffix': '.tar.gz',
            'download_name': f'lnd-darwin-amd64-{TARGET_LND_RELEASE}',
            'release_version': TARGET_LND_RELEASE,
            'daemon_name': 'lnd'
        }
    }
}
