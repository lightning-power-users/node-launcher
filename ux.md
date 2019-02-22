# The UX Vision for the Node Launcher

Website and Node Launcher user interface would be translated to at least every 
major language using Transifex.

1. User goes to LightningPowerUsers.com, the macOS App Store (or HomeBrew), the
Windows App Store, or their Linux package manager clicks the Download Node 
Launcher button that is front and center
2. User performs macOS dmg with installer app or Windows setup.exe install 
(this part needs to be filled in, there should be a configuration flow with 
Recommended nudges and Advanced options), installer flow ends with check marked 
"Open Node Launcher". I'd really want this to have a minimalist Default path 
where you can hit enter a couple of times and be done
3. An icon appears in their System Tray (top right on macOS, bottom right on 
Windows), with the a mini Node Launcher logo and an orange status dot. If the 
user clicks on it, they see a progress bar with "Syncing with the Lightning 
Network..." What the Node Launcher is doing in the background is using neutrino 
"SPV" to quickly sync Lightning, and launches bitcoind in the background so 
they can start syncing their full node. When the neutrino sync is done, the 
status dot becomes blue. When the bitcoind full node sync is done, LND connects 
to it directly and the status dot becomes green.
4. User receives a Node Launcher desktop notification to install the Joule 
browser extension, with a link to https://lightningjoule.com/
5. User installs Joule, and Joule automatically connects to the local LND node 
without any manual configuration at all
6. User receives a Node Launcher desktop notification to deposit BTC in their 
LND wallet, clicking it pops up a QR code  
7. User deposits BTC, channels automatically open
8. Node Launcher communicates estimated time before channels are open
9. User can now send satoshis with Joule!