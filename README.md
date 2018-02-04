Python NFC card reader for the Raspberry Pi, forked from https://github.com/mxgxw/MFRC522-python.

Sends check-in and check-out requests to the backend with http://docs.python-requests.org/en/master/.

## Requirements
This code requires you to have SPI-Py installed from the following repository:
https://github.com/lthiery/SPI-Py

```
sudo apt-get install python-dev

git clone https://github.com/lthiery/SPI-Py.git
cd SPI-Py
sudo python setup.py install
```

You may also need to add/uncomment `device_tree_param=spi=on` to `/boot/config.txt`.

## Pins for the NFC card reader
You can use [this](https://www.raspberrypi.org/documentation/usage/gpio-plus-and-raspi2/README.md) for reference.

| Name | Pin # | Pin name   |
|------|-------|------------|
| SDA  | 24    | GPIO8      |
| SCK  | 23    | GPIO11     |
| MOSI | 19    | GPIO10     |
| MISO | 21    | GPIO9      |
| IRQ  | None  | None       |
| GND  | Any   | Any Ground |
| RST  | 22    | GPIO25     |
| 3.3V | 1     | 3V3        |

#### Setup Guide

A good step-by-step guide can be found here:
http://raspmer.blogspot.co.at/2015/07/how-to-use-rfid-rc522-on-raspbian.html

## Pins for the LCD display

![LCD display](89u9crv.png)

## Environment Variables

The following environment variables need to be set, for example exported from a script in `/etc/profile.d/rc-check-in-env.sh`.
```
#!/bin/bash
export RC_CHECK_IN_SERVER='http://foo.bar/'
export RC_CHECK_IN_USERNAME=foo
export RC_CHECK_IN_PASSWORD=bar
```
## Startup

The card reader can be started by running `Read.py`. It can also be started automatically with the `rc-check-in-card-reader.service` service file.

```
git clone https://github.com/RefugeesCodeAT/rc-check-in-card-reader.git
cd rc-check-in-card-reader
sudo cp rc-check-in-card-reader.service /etc/systemd/system/
sudo systemctl enable rc-check-in-card-reader.service
sudo systemctl start rc-check-in-card-reader.service
```

### Related repositories:

Backend: https://github.com/RefugeesCodeAT/rc-check-in-backend  
Frontend: https://github.com/RefugeesCodeAT/Attendance

