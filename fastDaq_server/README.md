
# Configuring the Ethernet Connection

*Tested on Ubuntu 18.04.4 LTS, Ubuntu 18.04.5 LTS*

See the rc.local section to set up an ethernet connection that persists between computer reboots

### Shell script method ###

This is a quick way to make sure the struck daq is talking to the computer (via ethernet port)

The awful flaw with this method of connection is that you have to rerun the shell script *with sudo* if the computer and/or sis3316 ever reboots. To avoid this, we use the rc.local method below, which only requires sudo during the first configuration

Create shell script called `connect_ethernet.sh` with contents
```
#!/bin/bash
ifconfig enp1s0 down
ifconfig enp1s0 192.168.1.2
ifconfig enp1s0 up
arp -i enp1s0 -s 192.168.1.100 00:00:56:31:61:2C
# Network TCP/UDP tuning to support high-bandwith applications
#
sysctl -w net.core.rmem_max=8388608
sysctl -w net.core.wmem_max=8388608
sysctl -w net.core.rmem_default=65536
sysctl -w net.core.wmem_default=65536
#
sysctl -w net.ipv4.udp_mem='8388608 8388608 8388608'
#
sysctl -w net.ipv4.tcp_rmem='4096 87380 8388608'
sysctl -w net.ipv4.tcp_wmem='4096 65536 8388608'
sysctl -w net.ipv4.tcp_mem='8388608 8388608 8388608'
#
sysctl -w net.ipv4.route.flush=1
# Change jumbo frame size
ip link set enp1s0 mtu 9000
arp -a
```

Then check your ethernet port names

```
# List ethernet ports
$ifconfig -a
```

edit `enp1s0` in connect_ethernet.sh(https://osf.io/yfptz/) to what `ifconfig -a` tells you. You should also change the MAC address of shell script to match the one listed on the sis3316 daq (label on the back)

```bash
# Use chmod to make the shell script runnable
$chmod +x connect_ethernet.sh 
$sudo ./connect_ethernet.sh
# check to make sure things work
$ping 192.168.1.100
```
There should be a tiny flashing light on the struck daq while the ping command runs, and you should see some reasonable packet transfer

### rc.local method ###

This is the same idea as the section above, except runs on startup and keeps the ethernet connection persistent 

Obviously, like in the section above, you **have to change the ethernet port and sis3316 MAC address** from what I have.

First, edit the `/etc/network/interfaces` file (as sudo) to assign the IP address to the ethernet port on startup. Append the lines:

```
auto enp1s0
iface enp1s0 inet static
    address 192.168.1.2
```

Next, to keep the ethernet connection persistent, create the file `/etc/network/if-up.d/add-my-static-arp` (as sudo) with the contents

```
#!/bin/sh
arp -i enp1s0 -s 192.168.1.100 00:00:56:31:61:2C
```
Now make it executable

```bash
$sudo chmod +x /etc/network/if-up.d/add-my-static-arp
```

Then, create `/etc/rc.local` as sudo with the content below

```
#!/bin/sh -e
# Network TCP/UDP tuning to support high-bandwith applications
#
sysctl -w net.core.rmem_max=8388608
sysctl -w net.core.wmem_max=8388608
sysctl -w net.core.rmem_default=65536
sysctl -w net.core.wmem_default=65536
#
sysctl -w net.ipv4.udp_mem='8388608 8388608 8388608'
#
sysctl -w net.ipv4.tcp_rmem='4096 87380 8388608'
sysctl -w net.ipv4.tcp_wmem='4096 65536 8388608'
sysctl -w net.ipv4.tcp_mem='8388608 8388608 8388608'
#
sysctl -w net.ipv4.route.flush=1
#
# Change jumbo frame size
ip link set enp1s0 mtu 9000
#
exit 0
```
I found that this [web page](https://wwwx.cs.unc.edu/~sparkst/howto/network_tuning.php) explains the sysctl settings briefly

As a side note: Normally the payload size or MTU(Maximum Transfer Unit) is set to 1500 bytes. Jumbo frames can support to 9000 bytes per packet. If you change the value from 9000 to something else, make sure to update this setting in SIS3316/sis3316/sis3316_udp.py. To check your current size run `ip link show | grep mtu`

Create the file /etc/systemd/system/rc-local.service as sudo with the content:
```
[Unit]
 Description=/etc/rc.local Compatibility
 ConditionPathExists=/etc/rc.local

[Service]
 Type=forking
 ExecStart=/etc/rc.local start
 TimeoutSec=0
 StandardOutput=tty
 RemainAfterExit=yes
 SysVStartPriority=99

[Install]
 WantedBy=multi-user.target
```

Now, to make sure rc.local runs on startup
```bash
# Make it executable
$sudo chmod +x /etc/rc.local
# Enable rc.local and check its status
$sudo systemctl enable rc-local
$systemctl status rc-local # Should output an 'Active' status
```

Done! Now reboot and you should be able to `ping 192.168.1.100` immediately. Daq should remain ping-able through comp/daq reboots, just make sure that you don't change the ethernet port it's plugged into

### Aliases ###

For sanity's sake, it is also recommended to add an IP name to /etc/hosts. Just add the line `192.168.1.100  struckDaq` and you'll no longer have to type the IP address out. 

Or, just add an alias to your bashrc or bash_aliases `export STRUCKDAQ='192.168.1.100'`

### Troubleshooting ###

It is useful to make sure that the rc.local script is running without error with `$sudo /etc/rc.local start`

Make sure that the static IP that you assign in `/etc/network/interfaces` is NOT the same as the Default Route IP address of your internet connection, or else you will lose internet access

The sis3316 ought to be ping-able whether the computer falls asleep/not, or if the daq is turned off. If this is not the case, the arp table entry may not be persistent. (Run `arp` and if you don't see the ethernet connection anymore then this is the problem). I found this helpful forum post [here](https://askubuntu.com/questions/22998/add-static-arp-entries-when-network-is-brought-up)

### Additional Documentation ###
[SIS3316 Ethernet Addendum](https://osf.io/h2rvq/)

# Basic Usage Tutorial 

I'm assuming here you've already finished setting up the ethernet connection

To get the [sis3316 python library](https://github.com/dougUCN/SIS3316.git),

```
git clone https://github.com/dougUCN/SIS3316.git
```

After configuring the ethernet connection, turn on the sis3316 and check to see if the connection works using **tools/check_connection.py**. (If you ping'd the sis3316 successfully than there should be no issues)

```plaintext
usage: check_connection.py [-h] [-vme {2008,2007}] host [port]

Test sis3316 network connection.

positional arguments:
  host                  hostname or IP address
  port                  sis3316 destination port number (default: 1234)

optional arguments:
  -h, --help            show this help message and exit
  -vme {2008,2007}, --vme {2008,2007}
                        VME FPGA Version (default: 2008)
```

Port number doesn't matter. Host is `192.168.1.100` or `$STRUCKDAQ` or `struckDaq` or whatever you configured in the Ethernet connection section

### Loading in Config files

Every time you reboot the sis3316 you'll need to load in a config file. You can see current settings/load in config files/see documentation using **tools/conf.py**

```plaintext
usage: conf.py [-h] [--documentation] [-c CONFFILE] host [port]

Dump sis3316 configuration to a file (with -c loads configuration from file)

positional arguments:
  host                  hostname or IP address
  port                  UDP port number

optional arguments:
  -h, --help            show this help message and exit
  --documentation       Prints out documentation for possible arguments in
                        config file
  -c CONFFILE, --conf CONFFILE
                        Load configuration from file
```

There are a LOT of configuration options. Use the sis3316 manual and the --documentation flag. Config files are in a json format. [config.in](https://github.com/dougUCN/SIS3316/blob/master/tools/config.in) is an example

### Basic config file settings



### Struck readout

Once you have loaded in a configuration file and input, and have a signal running into the sis3316, run **tools/readout.py**

```plaintext
usage: readout.py [-h] [-c N [N ...]] [-o PATH] [-q] [--stats] host [port]

Read data from SIS3316. 
Write raw (binary) data to files (one file per channel).

positional arguments:
  host                  hostname or ip address.
  port                  UDP port number, default is 3333

optional arguments:
  -h, --help            show this help message and exit
  -c N [N ...], --channels N [N ...]
                        channels to read, from 0 to 15 (all by default). 
                        Use shell expressionsto specify a range (like "{0..7} {12..15}").
  -o PATH, --output PATH
                        a path for output, one file per channel.
                        default: "data/raw-ch"
  -q, --quiet           be quiet in stderr
  --stats               print statistics per channel (ignores --quiet)
```

# Working with the output binaries

tools/parse.py contains a function Parse that returns an iterator for events in a data file generated by tools/readout.py. See quickParse.py for an example of how to work with the binary