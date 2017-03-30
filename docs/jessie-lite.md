jessie lite
===========
Installation on jessie lite requires a few extra steps to install the missing dependancies.

This can be performed via ssh (if enabled), via a serial cable, or by connecting a keyboard and screen. A network connection is required.

Instructions below assume a fresh jessie lite install.

1. Update apt: `sudo apt-get update`
2. Upgrade packages: `sudo apt-get upgrade`
3. Install dependancies: `sudo apt-get install python-pip python-gpiozero`
4. Install a word list package e.g. `sudo apt-get install wbritish`
5. Install pwdgen:
   Either
    1. Install git: `sudo apt-get install git`
    2. clone repository: `git clone...`

   or download [pwdgen.py](../pwdgen.py) and [pwdgen.cfg](../pwdgen.cfg)
