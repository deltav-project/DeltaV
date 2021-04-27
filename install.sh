#!/bin/sh

# Run it with sudo !

mkdir /usr/local/bin/deltav
cp -r deltav/ /usr/local/bin/
cp deltav.service /etc/systemd/system/
