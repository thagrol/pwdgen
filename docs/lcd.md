LCD
===
pwdgen has built in support for most sizes of HD44780 LCDs. 1x16 and 40x4 are not currently supported.

To use an lcd connect it as shown below and enable it in pwdgen.cfg

| LCD pin   | GPIO (BCM numbering) |
|-----------|----------------------|
| Ground    | Ground               |
| Vin       | +5v                  |
| Contrast  | Ground               |
| RS        | 7                    |
| RW        | Ground               |
| D4        | 25                   |
| D5        | 24                   |
| D6        | 23                   |
| D7        | 18                   |
| EN        | 8                    |
| RS        | 7                    |
| Backlight | +5v                  |

LCD support is based on this: http://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/

HD44780 LCDs connected via i2c, spi, etc are not supported. LCDs must be directly connected to the GPIO pins.
