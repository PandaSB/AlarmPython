## Install DietPi
https://dietpi.com

For Raspberry Zero 2 : https://dietpi.com/downloads/images/DietPi_RPi234-ARMv8-Bookworm.img.xz

## Install on DietPi

apt-get install python3 python3-opencv python3-numpy python3-urllib3 python3-requests python3-libgpiod python3-python-telegram-bot python3-serial python3-smbus python3-paho-mqtt python3-luma.oled git openssl-client ppp pppconfig

cd /opt && git clone https://github.com/PandaSB/AlarmPython.git


### configure ppp
/etc/ppp/peers/provider
/etc/ppp/peers/simcom-pppd
```
/dev/ttyUSB2 115200
#Insert the username and password for authentication, default user and password are

user "" password ""
# The chat script, customize your APN in this file
connect 'chat -s -v -f /etc/ppp/peers/simcom-connect-chat'
# The close script
disconnect 'chat -s -v -f /etc/ppp/peers/simcom-disconnect-chat'
# Hide password in debug messages
hide-password
# The phone is not required to authenticate
noauth
# Debug info from pppd
debug
# If you want to use the HSDPA link as your gateway
defaultroute
# pppd must not propose any IP address to the peer
noipdefault
# No ppp compression
novj
novjccomp
noccp
ipcp-accept-local
ipcp-accept-remote
local
# For sanity, keep a lock on the serial line
lock
modem
dump
nodetach
# Hardware flow control
nocrtscts
remotename 3gppp
ipparam 3gppp
ipcp-max-failure 30
# Ask the peer for up to 2 DNS server addresses
usepeerdns
```

/etc/ppp/peers/simcom-connect-chat
```
ABORT "BUSY"
ABORT "NO CARRIER"
ABORT "NO DIALTONE"
ABORT "ERROR"
ABORT "NO ANSWER"
TIMEOUT 30
"" AT
OK ATE0
OK ATI;+CSUB;+CSQ;+CPIN?;+COPS?;+CGREG?;&D2
# Insert the APN provided by your network operator, default apn is 3gnet
OK AT+CGDCONT=1,"IP","free",,0,0
OK ATD*99#
CONNECT
```

/etc/ppp/peers/simcom-disconnect-chat
```
ABORT "ERROR"
ABORT "NO DIALTONE"
SAY "\nSending break to the modem\n"
"" +++
"" +++
"" +++
SAY "\nGoodbye\n"
```

cd /etc/systemd/system && wget https://gist.githubusercontent.com/rany2/330c8fe202b318cacdcb54830c20f98c/raw/404a2a7292afd402eb93ef055fe2f6893426fa6d/pppd@.service
cp /etc/systemd/system/pppd@.service /etc/systemd/system/pppd@provider.service
/etc/systemd/system/pppd@provider.service
```
[Unit]
Description=PPP connection for %I
Documentation=man:pppd(8)
StartLimitIntervalSec=0

Before=network.target
Wants=network.target
After=network-pre.target

[Service]
# https://github.com/ppp-project/ppp/commit/d34159f417620eb7c481bf53f29fe04c86ccd223
# otherwsise you can use 'forking' and replace 'up_sdnotify' with 'updetach'
Type=notify
ExecStart=/usr/sbin/pppd up_sdnotify nolog call %I
ExecStop=/bin/kill $MAINPID
ExecReload=/bin/kill -HUP $MAINPID
StandardOutput=null
# https://github.com/systemd/systemd/issues/481#issuecomment-544341423
Restart=always
RestartSec=1

# Sandboxing options to harden security
PrivateMounts=yes
PrivateTmp=yes
ProtectHome=yes
ProtectSystem=strict
# ProtectKernelTunables breaks IPv6 negotiation for PPP. Further PPP
# needs to set some kernel settings if certain options were applied.
ProtectKernelTunables=no
ProtectControlGroups=yes
# allow /etc/ppp/resolv.conf to be written when using 'usepeerdns'
ReadWritePaths=/run/ /etc/ppp/
AmbientCapabilities=CAP_SYS_TTY_CONFIG CAP_NET_ADMIN CAP_NET_RAW CAP_SYS_ADMIN
CapabilityBoundingSet=CAP_SYS_TTY_CONFIG CAP_NET_ADMIN CAP_NET_RAW CAP_SYS_ADMIN
KeyringMode=private
NoNewPrivileges=yes
# AF_NETLINK is needed to add an entry to the IP route table
RestrictAddressFamilies=AF_NETLINK AF_PACKET AF_UNIX AF_PPPOX AF_ATMPVC AF_ATMSVC AF_INET AF_INET6 AF_IPX
ProtectProc=invisible
RestrictNamespaces=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
RemoveIPC=yes
ProtectHostname=yes
ProtectClock=yes
ProtectKernelLogs=yes
ProtectKernelModules=yes
MemoryDenyWriteExecute=yes
LockPersonality=yes
SecureBits=no-setuid-fixup-locked noroot-locked
SystemCallFilter=@system-service
SystemCallArchitectures=native

# All pppd instances on a system must share a runtime
# directory in order for PPP multilink to work correctly. So
# we give all instances the same /run/pppd directory to store
# things in.
#
# For the same reason, we can't set PrivateUsers=yes, because
# all instances need to run as the same user to access the
# multilink database.
RuntimeDirectory=pppd
RuntimeDirectoryPreserve=yes

[Install]
WantedBy=multi-user.target
```

/etc/udev/rules.d/99-usb-serial.rules
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="ttySER0"
```
 

 /etc/systemd/system/alarm.service
 ```
[Unit]
Description=Alarm
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/opt/AlarmPython
ExecStart=/usr/bin/python3 /opt/AlarmPython/alarm.py
KillSignal=SIGINT
Restart=always
 ```
systemctl daemon-reload
systemctl enable alarm.service
