pwdgen
======
If you're like me you have many accounts scattered across the internet that need logins. Current advice seems to be to use unique passwords for every account. 

Managing lots of passwords, while not always easy, is only half the problem and there exist many tools to assist in doing so. This project attempts to address the other half of the problem: coming up with the passwords.

Inspired by https://xkcd.com/936/

Basic Installation and Usage
----------------------------
Requirements:
* a raspberry pi
* a microSD card with
  * raspbian jessie
  * gpiozero
  * one of the packages listed [here](https://packages.debian.org/jessie/wordlist)
 
Installation:
1. clone this repository or download pwdgen.py and pwdgen.cfg
2. make sure pwdgen.py and pwdgen.cfg are in the same directory
3. make sure pwdgen.py has execute permission
4. if required edit the options in pwdgen.cfg

Usage:
`./pwdgen.py`
For basic help: `pwdgen.py -h`

Advanced Usage
--------------
See
* [docs/lcd.md](docs/lcd.md)
* [docs/push_button.md](docs/push_button.md)
* [docs/usb_keyboard.md](docs/usb_keyboard.md)
* [docs/password_dongle.md](docs/password_dongle.md)
* [docs/jessie-lite.md](docs/jessie-lite.md)

Notes
-----
Don't blame me if you get a password you consider offensive. The are just too many possibilities to even attempt to filter themout.

[hidsetup.sh](hidsetup.sh) is derrived from here: http://isticktoit.net/?p=1383

LCD support is based on this: http://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/