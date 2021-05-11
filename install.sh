#!/bin/sh

# Run it with sudo !

cp -r deltav/ /usr/local/bin/
cp deltav.service /etc/systemd/system/
cp 83-capture-card.rules /etc/udev/rules.d/
