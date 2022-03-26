# DeltaV
LED extend colored background for TV.

## Hardware used

- Raspberry Pi 3 B+
- Avermedia Live Gamer Portable 2 PLUS - GC513
- Addressable leds strip (32 leds soldered in series) connection to the raspberry GPIO via 3 cables (D OUT, 5V, GROUND)

*NB : We used individual velcro pads on each led to attach the strip at the back of the display*

## Install

Run `sudo ./install.sh` from this repo directory.

## Run

Auto launch at capture card connection / boot if capture card is already connected.

Can be manually started with `sudo systemctl start deltav.service`.

Type `sudo journalctl -u deltav` to check for service logs.
