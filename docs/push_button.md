Push Button
===========

pwdgen has support for generating passwords at the push of a button:

1. Connect a suitable push button (SPST push to make non-locking) between GPIO 19 and ground.
2. Enabled the button support in pwdgen.cfg
3. Start pwdgen: `./pwdgen.py &`

A short press will generate a set of passwords to all enabled output devices.
A long (> 3 seconds) press issues a `sudo poweroff` command

The GPIO pin can be configured in pwdgen.cfg.

If no convienent ground pins is avaiable, an arbitary GPIO pin may be used by setting "ground_pin" in pwdgen.cfg.

On a Pi Zero or ZeroW a 6mm tactile switch will fit directly between GPIO 19 and the ground at the nearest end of the same row.