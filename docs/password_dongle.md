Making a USB Password Generator Dongle
======================================

With a little efort, a raspberry pi zero/zeroW, a small microSD card and a push button it is possible to put together a simple to use USB dongle for generating passwords.

The Easy Way
------------
* Grab pwdpi.zip from [Releases](../Releases).
* Unzip and burn pwdpi.img to a microSD card. 1GB may work, 2GB will definitely be OK.
* If required edit pwdgen.cfg in the boot partition
* Connect a push button between GPIO 19 and ground
* Connect your pi to the host with a standard micro USB cable.
* Open a text editor and press a button to generate some passwords.

The Not So Easy Way
-------------------
* Burn jessie-lite onto a microSD card.
* Follow the instructions in [jessie-lite.md](jessie-lite.md), [push_button.md](push_button.md), [usb_keyboard.md](usb_keyboard.md), and optionally [lcd.md](lcd.md)

To make the pi more resilient, take a look at http://wiki.psuter.ch/doku.php?id=solve_raspbian_sd_card_corruption_issues_with_read-only_mounted_root_partition