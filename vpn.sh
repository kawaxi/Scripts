#!/usr/bin/expect -f

cd "lab-connection"

spawn openvpn OS-213**-OSCP.ovpn
expect "Enter Auth Username:" {
send "OS-213**\n"
}
expect "Enter Auth Password:" {
    send "mypass\n"
}
interact
secret 12313412412341dsadsad324c
aws_secret=121kasdjasdj12394kai902m