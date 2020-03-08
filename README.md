# cometblue-domoticz
Domoticz plugin to control your Comet Blue radiator valve over bluetooth with Domoticz by using the script written by Torsten Tränkner (https://www.torsten-traenkner.de/wissen/smarthome/heizung.php)

You can buy this devices under different names: Xavax Hama, Sygonix HT100 BT, Eurotronic Comet Blue.

<h1>Instructions:</h1>

The plugin was tested on a Raspberry Pi 3 with integrated bluetooth.

<h2>Installing Prerequisites</h2>
<h3>Installing Domoticz</h3>
<pre><code>
curl -L https://install.domoticz.com | bash
</code></pre>

<h3>Make sure your Domoticz plugin system runs properly</h3>
<pre><code>
python3 -V
apt-get install python3.x libpython3.x python3.x-dev #(where 'x' is the version from above: e,g libpython3.7)
</code></pre>

<h3>Installing prerequisites for this plugin</h3>
<pre><code>
apt-get install bluez bluetooth expect
wget https://www.torsten-traenkner.de/wissen/smarthome/heaterControl.exp
chmod 755 heaterControl.exp
cp heaterControl.exp /usr/local/bin/
</code></pre>

<h2>Installing the Domoticz plugin</h2>

<pre><code>cd domoticz/plugins
git clone https://github.com/damsma/cometblue-domoticz.git
systemctl restart domoticz
</code></pre>

<h2>Adding the radiator valve device to domiticz</h2>

First you have to find out the Bluetooth Device Address of your device:
<pre><code>hciconfig hci0 up
hcitool lescan
</code></pre>

This will give you the list of found devices, search for the device named "Comet Blue" and copy the adress, it will look something like this:
<pre><code>A0:B0:C0:D0:E0:D0 Comet Blue
</code></pre>

In Domoticz go to setup->hardware, select the plugin "Comet Blue radiator valve (cometblue-domoticz)", fill out this three fields:
- Bluetooth Device Address <- the address you found before
- Pin-Code <- in this version, you have to type in the pin code in little endian format (see https://www.torsten-traenkner.de/wissen/smarthome/heizung.php), for a new device this will be 00000000
- Poll interval <- the interval in seconds, how often the plugin will request the actual temperature from the device

<b>Done! The plugin will now create 2 new devices for you in domoticz:</b>
- temperature device <- shows the actual temperature of the room
- utility device <- for temperature control

<h1>Troubleshooting</h1>
If you experience problems with other plugins that uses Bluetooth (e,g Xiaomi Mi Flora plugin), remove this 3 lines in heaterControl.exp:
<pre><code>exec hciconfig hci0 down
</code></pre>
