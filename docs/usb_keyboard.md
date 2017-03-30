USB (HID) Keyboard
==================

pwdgen can emulate a USB HID keyboard and send generated passwords to a host computer as key events.

Some additional setup of raspbian is required but no drivers are needed on the host. This functionality works best when combined with a [push button](push_button.md).

Requirements
------------
This has only been tested on Pi Zero and Pi ZeroW. It may work on an A or A+ if it can be put into gadget mode. **This will not work on a B, B+, 2, or 3 as they do not support gadget mode (the USB hub/ethernet chip gets in the way).**

In addition to pwdgen.py and pwdgen.cfg, the files [10-hidg.rules](../10-hidg.rules) and [hidsetup.sh](../hidsetup.sh) are needed.

Installation
------------
* Add 'dtoverlay=dwc2' to /boot/config.txt
* Install the hid gadget rules: `sudo cp 10-hidg.rules /etc/udev/rules.d`
* Arrange for hidsetup.sh to be run by root at every boot:
  * `sudo nano /etc/rc.local`
  * add '/path/to/hidsetup.sh &' above the line that reads 'exit 0'
* Edit pwdgen.cfg and enabled hidkeyboard support.
* Optionally run pwdgen at start up:
  * `sudo nano /etc/rc.local`
  * add 'su - pi -c "/path/to/pwdgen.py" &' above the line that reads 'exit 0' and after any call to hidsetup.sh

Usage
-----
* Set up a [push button](push_button.md)
* Using a standard micro usb cable connect the pi to the host system.
* Once pi has booted and host has detected it as a keyboard:
  * Open your favourite text editior
  * press the button
* press and hold the button to safely shutdown the pi.

Notes
-----
There is experimental support for launching an application on the host computer. Enable at your own risk. There is no feedback from the host to the pi to say that the app has correctly started so weird stuff may happen.

