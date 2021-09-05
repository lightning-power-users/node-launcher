# The UX Vision for the Node Launcher

Website and Node Launcher user interface would be translated to at least every 
major language using Transifex.

## Initialization process

1. User goes to LightningPowerUsers.com, the macOS App Store (or HomeBrew), the
Windows App Store, or their Linux package manager clicks the Download Node 
Launcher button that is front and center
2. User performs macOS dmg with installer app or Windows setup.exe / MSI Package
install (this part needs to be filled in, there should be a configuration flow 
with Recommended nudges and Advanced options), installer flow ends with check 
marked "Open Node Launcher". It should be a single step process for people who
just want defaults: a single button "Install now" that installs it immediatelly
and "Configure installation" button for advanced users.
3. An icon appears in their System Tray (top right on macOS, bottom right on 
Windows), with the a mini Node Launcher logo and an orange status dot. If the 
user clicks on it, they see a progress bar with "Syncing with the Lightning 
Network..." What the Node Launcher is doing in the background is using neutrino 
"SPV" to quickly sync Lightning. A notification is shown to the user requesting
him to choose between pruning and non-pruning mode. Pruning is the default,
recommended setting. Non-pruning is disbled if the user has less than 300GB of
free disk space. A compuer parameter scan is started in parallel to determine
the best configuration for dbcache etc. Once the user confirms the setting
bitcoind is launched in the background so they can start syncing their full node.
When the neutrino sync is done, the status dot becomes blue. When the bitcoind
full node sync is done, LND connects to it directly and the status dot becomes
green. Both nodes default to using Tor.
4. User receives a Node Launcher desktop notification to install the Joule 
browser extension, with a link to https://lightningjoule.com/
5. User installs Joule, and Joule automatically connects to the local LND node 
without any manual configuration at all
6. User receives a Node Launcher desktop notification to deposit BTC in their 
LND wallet, clicking it pops up a QR code. The notification has orange warning
that it's currently unsuitable for large amounts. After clicking more info, the
user is informed that they should wait for sync to be finished and to purchase HW
wallet for savings. Additionally a checkbox "Unlink bitcoins" is present and
checked by default. Wasabi or Joinmarket tool is used in the background to unlink
the deposited bitcoins before opening the channels if the checkbox is checekd.
7. User deposits BTC, channels automatically open
8. Node Launcher communicates estimated time before channels are open
9. User can now send satoshis with Joule!

## Upgrade process

1. If the package is installed using a package manager, automatic updates for the
package are disabled by default using post-install script in order to prevent
consensus attacks.
2. When a new update is available, the user is informed about it and a window asking
confirmation appears. The window contains information about how many developers
of the launcher signed that the upgrade is OK and what is the total number of
developers needed. If the number is lower than half, the update is ignored. User can
explicitly install it from the menu, but is warned about potential consequences.
The update window also contains "detailed information" button. The button shows a list
of developers that signed the release and the release notes. The top of release notes
contains information about whether changes to consensus were made.
3. If the user confirms the update, the launcher synchronizes with package manager in
order to make sure an unmodified package is installed. Then instructs it to download
the package, but not install it yet. A minute before expected finish of download all
relevant processes are terminated. The package is backed up together with channel data
and everything else. The new package is installed and launched. In case of any prolem,
the user can restore the package by opening a restore tool present in the backup
data.

## Using HW wallet

1. If the user inserts HW wallet, he's instructed to initialize it if it isn't already.
2. A new "savings" account appears. The user can deposit to it from checking account
(with auto-mix by default if the coins were involved in channels at some point or
weren't mixed before) or directly (auto-mix by default). A warning is issued if bitcoind
isn't synced yet. "Show on Trezor" feature is used by default if the user selects direct
deposit without mixing (would be great if we could mix with HW wallets directly , though).
3. After the user deposits coins, they are mixed if needed and sent to the HW wallet.
4. The user can move coins from savings account to checking account at any time. Mixing is
suggested by default if the coins weren't mixed.

## Export to Rpi feature.

The user can simply export his LND instance to a RPi or a similar computer by running the
export tool. Bitcoind and lnd data are exported in that case. Everything else is
reconfigured to use the RPi fter successful export.

1. The user selects export tool and is instructed to insert SD card and optionally an
external HDD/SSD (for the blockchain in case of non-pruning node).
2. A recent image of the OS is downloaded and initialization script is added to startup.
3. Data is copied over. Data includes keys for communicating between the node and the
computer.
4. SD card and HDD is unmounted, the internal nodes are disabled and the user can move
the card to RPi and start it.
5. Once the node starts, it's found automatically by the computer and connected. All
wallet frontends are redirected to it. The user can choose to delete old data from his
computer (bitcoind with its dir, lnd, with everything except the keys/channels).

## Additional apps (plugins) feature

The launcher should allow users to download other plugins and make them work directly with
the blockchain and wallets. In case the user use the export feature, the plugins can
install their backends on RPi as well and communicate using secured channel.

Some plugins that might be useful: Btcpay server, OpenBazaar, Lighthouse, Bitmessage.

## Identity management

The user should be allowed to create new identities that are completely separated from
each other. They'd share bitcoind as source of data, but wouldn't interact otherwise. If
the user attemptes to move funds between them, mixing is mandatory. (It should be detected
that the user entered the address of one identity into "send" field of another.)

In case the user exported their node, family members and other devices should be able to
reuse it if he grants them access. They can either share funds (family budget), or separate
them.
