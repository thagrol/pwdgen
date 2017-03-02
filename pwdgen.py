#!/usr/bin/env python

####
## tool to generate random passwords
## inspired by https://xkcd.com/936/
##
## no guarantees, express or implied
## use at own risk
## non-commercial use only
####

## imports
import argparse
import ConfigParser
import logging
import os
import random
import sys
import textwrap
import threading
import time

import gpiozero


## clases
class lcd(object):
    """base class for all output devices"""

    def __init__(self, enabled=True):
        self.__enabled = enabled

    def reset(self):
        pass

    def write(self, line, message):
        """write message to display"""
        pass

    def close(self):
        """clean up"""
        pass
    
class hd44780(lcd):
    """hd44870 lcd

    Based on code from http://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/
    Rewritten to use gpiozero instead of RPi.GPIO
    """

    CHR = True
    CMD = False
    PULSE = 0.0005
    DELAY = 0.0005

    def __init__(self,
                 enabled=False,
                 rows=None,
                 cols=None,
                 d4=None,
                 d5=None,
                 d6=None,
                 d7=None,
                 en=None,
                 rs=None):
        
        self.__enabled = enabled
        self.__rows = rows
        self.__cols = cols
        self.__d4 = d4
        self.__d5 = d5
        self.__d6 = d6
        self.__d7 = d7
        self.__en = en
        self.__rs = rs

        lcdsize = '%sx%s' % (self.__cols, self.__rows)
        logging.debug('LCD size %s' % lcdsize)
        # configure lcd line start addresses
        # only 16x2 has been tested. I don't have access to other sizes
        if ( lcdsize == '16x2'
             or lcdsize == '20x2'
             or lcdsize == '40x2' ):
            self.__lineaddr = {1:0x80,
                               2:0xC0}
        elif lcdsize == '16x4':
            self.__lineaddrs = {1:0x80,
                                2:0xC0,
                                3:0x90,
                                4:0xD0}
        elif lcdsize == '20x4':
            self.__lineaddrs = {1:0x80,
                                2:0xC0,
                                3:0x94,
                                4:0xD4}
        else:
            logging.warning('Unsupported LCD size (%s). HD44780 output disabled.' % lcdsize)
            self.__enabled = False

        if self.__enabled:
            # setup gpio
            self.__lcdpins = {'d4':gpiozero.OutputDevice(self.__d4),
                              'd5':gpiozero.OutputDevice(self.__d5),
                              'd6':gpiozero.OutputDevice(self.__d6),
                              'd7':gpiozero.OutputDevice(self.__d7),
                              'en':gpiozero.OutputDevice(self.__en),
                              'rs':gpiozero.OutputDevice(self.__rs)
                              }
            self.reset()
        
        return

    def reset(self):
        """reset lcd"""
        if self.__enabled:
            self.__sendbyte(0x33, hd44780.CMD)
            self.__sendbyte(0x32, hd44780.CMD)
            self.__sendbyte(0x06, hd44780.CMD)
            self.__sendbyte(0x0C, hd44780.CMD)
            self.__sendbyte(0x28, hd44780.CMD)
            self.__sendbyte(0x01, hd44780.CMD)
            time.sleep(hd44780.DELAY)

    def write(self, line, message):
        """write message to display"""
        if self.__enabled and line <= self.__rows:
            message = message.ljust(self.__cols, ' ')
            self.__sendbyte(self.__lineaddrs[line], hd44780.CMD)
            for i in range(self.__cols):
                self.__sendbyte(ord(message[i]), hd44780.CHR)
                
    def close(self):
        """clean up"""
        for v in self.__lcdpins.itervalues():
            v.close()
        self.__lcdpins.clear()
        self.__enabled = False

    def __sendbyte(self, data, mode):
        """send byte to lcd"""
        
        if self.__enabled:
            # set mode
            self.__lcdpins['rs']. value = mode
            # send high bits
            self.__lcdpins['d4'].off()
            self.__lcdpins['d5'].off()
            self.__lcdpins['d6'].off()
            self.__lcdpins['d7'].off()
            if data&0x10==0x10:
                self.__lcdpins['d4'].on()
            if data&0x20==0x20:
                self.__lcdpins['d5'].on()
            if data&0x40==0x40:
                self.__lcdpins['d6'].on()
            if data&0x80==0x80:
                self.__lcdpins['d7'].on()
            # clock out the bits
            self.__blipenable()
            # send low bits
            self.__lcdpins['d4'].off()
            self.__lcdpins['d5'].off()
            self.__lcdpins['d6'].off()
            self.__lcdpins['d7'].off()
            if data&0x01==0x01:
                self.__lcdpins['d4'].on()
            if data&0x02==0x02:
                self.__lcdpins['d5'].on()
            if data&0x04==0x04:
                self.__lcdpins['d6'].on()
            if data&0x08==0x08:
                self.__lcdpins['d7'].on()
            # clock out the bits
            self.__blipenable()

    def __blipenable(self):
        """blip the lcd enable pin"""
        if self.__enabled:
            time.sleep(hd44780.DELAY)
            self.__lcdpins['en'].on()
            time.sleep(hd44780.PULSE)
            self.__lcdpins['en'].off()
            time.sleep(hd44780.DELAY)

class console(lcd):
    """console output"""

    def __init__(self, enabled=True):
        self.__enabled = enabled

    def write(self, line, message):
        """write message to display"""
        if self.__enabled:
            print message

class hidkey(lcd):
    """simplified usb HID keyboard"""

    # map characters to usb hid reports
    keymap = { 'keyup':bytearray([0,0,0,0,0,0,0,0]),
               'return':bytearray([0,0,0x28,0,0,0,0,0]),
               'a':bytearray([0,0,0x04,0,0,0,0,0]),
               'b':bytearray([0,0,0x05,0,0,0,0,0]),
               'c':bytearray([0,0,0x06,0,0,0,0,0]),
               'd':bytearray([0,0,0x07,0,0,0,0,0]),
               'e':bytearray([0,0,0x08,0,0,0,0,0]),
               'f':bytearray([0,0,0x09,0,0,0,0,0]),
               'g':bytearray([0,0,0x0A,0,0,0,0,0]),
               'h':bytearray([0,0,0x0B,0,0,0,0,0]),
               'i':bytearray([0,0,0x0C,0,0,0,0,0]),
               'j':bytearray([0,0,0x0D,0,0,0,0,0]),
               'k':bytearray([0,0,0x0E,0,0,0,0,0]),
               'l':bytearray([0,0,0x0F,0,0,0,0,0]),
               'm':bytearray([0,0,0x10,0,0,0,0,0]),
               'n':bytearray([0,0,0x11,0,0,0,0,0]),
               'o':bytearray([0,0,0x12,0,0,0,0,0]),
               'p':bytearray([0,0,0x13,0,0,0,0,0]),
               'q':bytearray([0,0,0x14,0,0,0,0,0]),
               'r':bytearray([0,0,0x15,0,0,0,0,0]),
               's':bytearray([0,0,0x16,0,0,0,0,0]),
               't':bytearray([0,0,0x17,0,0,0,0,0]),
               'u':bytearray([0,0,0x18,0,0,0,0,0]),
               'v':bytearray([0,0,0x19,0,0,0,0,0]),
               'w':bytearray([0,0,0x1A,0,0,0,0,0]),
               'x':bytearray([0,0,0x1B,0,0,0,0,0]),
               'y':bytearray([0,0,0x1C,0,0,0,0,0]),
               'z':bytearray([0,0,0x1D,0,0,0,0,0]),
               '1':bytearray([0,0,0x1E,0,0,0,0,0]),
               '2':bytearray([0,0,0x1F,0,0,0,0,0]),
               '3':bytearray([0,0,0x20,0,0,0,0,0]),
               '4':bytearray([0,0,0x21,0,0,0,0,0]),
               '5':bytearray([0,0,0x22,0,0,0,0,0]),
               '6':bytearray([0,0,0x23,0,0,0,0,0]),
               '7':bytearray([0,0,0x24,0,0,0,0,0]),
               '8':bytearray([0,0,0x25,0,0,0,0,0]),
               '9':bytearray([0,0,0x26,0,0,0,0,0]),
               '0':bytearray([0,0,0x27,0,0,0,0,0]),
               '!':bytearray([0x02,0,0x1e,0,0,0,0,0]),
               '#':bytearray([0x02,0,0x20,0,0,0,0,0]),
               '$':bytearray([0x02,0,0x21,0,0,0,0,0]),
               '%':bytearray([0x02,0,0x22,0,0,0,0,0]),
               '&':bytearray([0x02,0,0x24,0,0,0,0,0]),
               '.':bytearray([0,0,0x37,0,0,0,0,0]),
               '?':bytearray([0x02,0,0x38,0,0,0,0,0])
               }

    def __init__(self,device, enabled=True):
        self.__enabled = enabled
        self.__device = device

    def write(self, line, message):
        """write message to display"""
        if self.__enabled:
            try:
                with open(self.__device, 'w') as d:
                    for c in message:
                        d.write(hidkey.keymap[c])
                        d.write(hidkey.keymap['keyup'])
                    d.write(hidkey.keymap['return'])
                    d.write(hidkey.keymap['keyup'])
                    d.flush()
            except KeyboardInterrupt:
                raise
            except:
                logging.exception('error writing to hid keyboard')
                self.__enabled = False

class cmdbutton(object):

    def __init__(self, cfg, lcds, wordlist, rng):
        self.__button = gpiozero.Button(cfg['button_pin'], pull_up=True,
                                        bounce_time=0.025,
                                        hold_time=2)
        self.__press_time = None

        self.__button.when_held = self.__on_hold
        self.__button.when_pressed = self.__on_press
        self.__button.when_released = self.__on_release

        self.__cfg = cfg
        self.__lcds = lcds
        self.__wordlist = wordlist
        self.__rng = rng
        self.__groundpin = self.__cfg['button_ground']
        if self.__groundpin != -1:
            # this is to allow the use of an arbitrary gpio as
            # ground for the button
            self.__ground = gpiozero.OutputDevice(self.__groundpin,
                                                  initial_value=False)
        else:
            self.__ground = None

    def run(self):
        while g_run_threads:
            time.sleep(1)
        self.__button.close()
        try:
            self.__ground.close()
        except:
            pass
    
    def __on_press(self):
        # button pressed
        self.__press_time = time.time() - self.__button.active_time

    def __on_release(self):
        # short press
        if time.time() - self.__press_time < 2:
            outputpasswords(genpasswords(self.__wordlist, self.__rng, self.__cfg),
                            self.__lcds)

    def __on_hold(self):
        # button held
        os.system('sudo poweroff')
        sys.exit(0)


## functions
def getconfig(configfile='pwdgen.cfg'):
    """Get config from file"""

##config dictionary keys:
##    button_enabled
##    button_ground
##    button_pin
##    hdd44780_cols
##    hdd44780_d4
##    hdd44780_d5
##    hdd44780_d6
##    hdd44780_d7
##    hdd44780_en
##    hdd44780_rows
##    hdd44780_rs
##    hidkey_device
##    hidkey_enabled
##    lcd_enabled
##    lcd_type
##    lcdproc_host
##    lcdproc_port
##    pwd_case
##    pwd_dict
##    pwd_generate
##    pwd_leet
##    pwd_maxlength
##    pwd_minlength
##    pwd_prefixd
##    pwd_seperator
##    pwd_suffixd
##    pwd_words

    # default values
    defaults = {'dict':'/usr/share/dict/words',
                'minlength':'4',
                'maxlength':'7',
                'words':'2',
                'seperator':'.',
                'generate':'3',
                'leet':'no',
                'prefix_digits':'0',
                'suffix_digits':'0',
                'case':'lower',

                'enabled':'no',

                'host':'127.0.0.1',
                'port':'13666',
                
                'ground_pin':'-1'}
    
    cp = ConfigParser.SafeConfigParser(defaults)
    config_list = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'pwdgen.cfg'),
                   configfile]

    read = cp.read(config_list)
##    if len(read) == 0:
##        configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'pwdgen.cfg')
##        read == cp.read(configfile)
    if len(read) == 0:
        logging.error('Unable to read config file.')
        sys.exit('Unable to read config file.')
            
    config = {}

    # password section
    # all needed so don't trap any exceptions
    config['pwd_dict'] = cp.get('password', 'dict')
    config['pwd_minlength'] = cp.getint('password', 'minlength')
    config['pwd_maxlength'] = cp.getint('password', 'maxlength')
    config['pwd_words'] = cp.getint('password', 'words')
    config['pwd_seperator'] = cp.get('password', 'seperator')
    # seperator is not currently validated
    # it should be restricted to a-z 0-9 and !$%&*.?-_
    config['pwd_generate'] = cp.getint('password', 'generate')
    config['pwd_leet'] = cp.getboolean('password', 'leet')
    config['pwd_prefixd'] = cp.getint('password', 'prefix_digits')
    config['pwd_suffixd'] = cp.getint('password', 'suffix_digits')
    config['pwd_case'] = cp.get('password', 'case')

    # lcd section
    try:
        config['lcd_enabled'] = cp.getboolean('lcd', 'enabled')
        if config['lcd_enabled']:
            config['lcd_type'] = cp.get('lcd', 'type').lower()
    except KeyboardInterrupt:
        raise
    except:
        # broken or missing lcd config
        logging.warning("Unabled to read lcd config")
        config['lcd_enabled'] = False

    # lcd config
    if config['lcd_enabled']:
        if config['lcd_type'] == 'hd44780':
            # hd44780 lcd
            try:
                config['hdd44780_rows'] = cp.getint('hd44780', 'rows')
                config['hdd44780_cols'] = cp.getint('hd44780', 'cols')
                config['hdd44780_d4'] = cp.getint('hd44780', 'd4')
                config['hdd44780_d5'] = cp.getint('hd44780', 'd5')
                config['hdd44780_d6'] = cp.getint('hd44780', 'd6')
                config['hdd44780_d7'] = cp.getint('hd44780', 'd7')
                config['hdd44780_en'] = cp.getint('hd44780', 'en')
                config['hdd44780_rs'] = cp.getint('hd44780', 'rs')
            except KeyboardInterrupt:
                raise
            except:
                # broken or missing config
                logging.warning("Unabled to read hd44780 config")
                config['lcd_enabled'] = False
        elif config['lcd_type'] == 'lcdproc':
            # LCDProc
            try:
                config['lcdproc_host'] = cp.get('lcdproc', 'host')
                config['lcdproc_port'] = cp.get('lcdproc', 'port')
                logging.warning('LCDProc not currently supported.')
                config['lcd_enabled'] = False
            except KeyboardInterrupt:
                raise
            except:
                # broken or missing config
                logging.warning("Unabled to read lcdproc config")
                config['lcd_enabled'] = False
        else:
            # unknow lcd type
            config['lcd_enabled'] = False

    # button section
    try:
        config['button_enabled'] = cp.getboolean('button', 'enabled')
        config['button_pin'] = cp.getint('button', 'sense_pin')
        try:
            config['button_ground'] = cp.getint('button', 'ground_pin')
        except (ValueError, ConfigParser.NoOptionError):
            config['button_ground'] = -1
    except KeyboardInterrupt:
        raise
    except:
        logging.exception("Unabled to read button config")
        config['button_enabled'] = False

    # hidkeyboard section
    try:
        config['hidkey_enabled'] = cp.getboolean('hidkeyboard', 'enabled')
        config['hidkey_device'] = cp.get('hidkeyboard', 'device')
    except KeyboardInterrupt:
        raise
    except:
        logging.exception("Unabled to read hidkeyboard config")
        config['button_enabled'] = False

    return config

def getargs():
    """parse and return cmdline args"""

    parser = argparse.ArgumentParser(description='Generate random passwords.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''\
    lcd settings must be configured in pwdgen.cfg.
    -k only functions on models capable of running in USB gadget more and where gadget mode has been correctly comfigured.
    If none of -q, -l, -k, and -c are specified output will be to all devices enabled in pwdgen.cfg.

    Additional options are available in pwdgen.cfg
    Where apropriate, command line options override pwdgen.cfg'''))
    oh = 'generate one set of passwards and exit. Ignored if a push button has not been enabled (see pwdgen.cfg).'
    parser.add_argument('-o','--once',
                        action='store_true',
                        help=oh)
    parser.add_argument('-d','--debug',
                        action='store_true',
                        help='enabled debug output')
    parser.add_argument('-w','--words',
##                        default=cfg['pwd_words'],
                        default='-1',
                        type=int,
                        help='number of words in each password.')
    parser.add_argument('passwords',
                        type=int,
                        nargs='?',
##                        default=cfg['pwd_generate'],
                        default='-1',
                        help='number of passwords to generate.')
    ex_group = parser.add_mutually_exclusive_group()
    ex_group.add_argument('-q','--quiet',
                          action='store_true',
                          help='suppress console outport. Does not suppress --debug')
    ex_group.add_argument('-c','--console',
                          action='store_true',
                          help='output passwords to console only.')
    ex_group.add_argument('-l','--lcd',
                          action='store_true',
                          help='output passwords to LCD only. Implies -q.')
    ex_group.add_argument('-k','--keyboard',
                          action='store_true',
                          help='output passwords to USB Keyboard only. Implies -q.')

    args =  parser.parse_args()
    return args

def getopts():
    """get options from config file and command line"""

    args = getargs()
    # not entirely happy having this here
    # but it needs to be setup as soon as possible
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        
    config = getconfig()

    # args override config
    if args.console:
        config['lcd_enabled'] = False
        config['hidkey_enabled'] = False
    if args.lcd:
        args.quiet = True
        config['hidkey_enabled'] = False
    if args.keyboard:
        args.quiet = True
        config['lcd_enabled'] = False
    if args.words != -1:
        config['pwd_words'] = args.words
    if args.passwords != -1:
        config['pwd_generate'] = args.passwords

    if config['button_enabled'] != True:
        args.once = True
        
##    config['pwd_words'] = args.words
##    config['pwd_generate'] = args.passwords

    return config, args

def loadwordlist(source, min_length, max_length):
    """load word list from source file"""

    wordlist = []
    with open(source, 'r') as s:
        for l in s.readlines():
            l = l.rstrip()
            if l.isalpha() and len(l) >= min_length and len(l) <= max_length:
                wordlist.append(l.lower())

    return wordlist

def getword(wordlist, rng):
    """return random word from wordlist"""
    return wordlist[rng.randrange(len(wordlist))]

def genpwd(wordlist, rng, cfg):
    """generate random password"""
    sep = cfg['pwd_seperator']
    wl = []
    for n in range(cfg['pwd_words']):
        while True:
            w = getword(wordlist, rng)
            if w not in wl:
                wl.append(w)
                break
    newpwd = ''
    for i in wl:
        newpwd += i
        newpwd += sep[rng.randrange(len(sep))]
    newpwd = newpwd[:-1]
    # password mangling
    # digit prefix
    prefix = ''
    if cfg['pwd_prefixd'] > 0:
        for i in range(cfg['pwd_prefixd']):
            prefix += str(rng.randint(0, 9))
    # digit suffix
    suffix = ''
    if cfg['pwd_suffixd'] > 0:
        for i in range(cfg['pwd_suffixd']):
            suffix += str(rng.randint(0, 9))
    newpwd = prefix + newpwd + suffix
    # leet speak
    if cfg['pwd_leet']:
        newpwd = leet(newpwd)
    # letter case
    if cfg['pwd_case'] == 'lower':
        newpwd = newpwd.lower()
    elif cfg['pwd_case'] == 'upper':
        newpwd = newpwd.upper()
    elif cfg['pwd_case'] == 'title':
        newpwd = newpwd.title()
    elif cfg['pwd_case'] == 'random':
        for l in newpwd:
            if rng.random() > 0.5:
                vnewpwd += l.upper()
            else:
                vnewpwd += l.lower()
        newpwd = vnewpwd
        
    return newpwd

def leet(text):
    """translate text to leet"""

    leetswap = {'a':'4',
                'e':'3',
                'i':'1',
                'o':'0',

                'l':'1',
                's':'5',
                't':'7'}

    for n, l in leetswap.iteritems():
        text = text.replace(n, l)
    return text

def genpasswords(wordlist, rng, cfg):
    """generate passwords"""
    pwdlist = []        
    for i in range(cfg['pwd_generate']):
        pwdlist.append(genpwd(wordlist, rng, cfg))
        
    return pwdlist

def outputpasswords(passwords, devices):
    """write passwords to configured devices"""
    i = 1
    for p in passwords:
        for d in devices:
            d.write(i, p)
        i += 1


## main   
if __name__ == '__main__':
    try:
        rng = random.SystemRandom()
        g_run_threads = True
        cfg, args = getopts()

        lcds = []
        # console output
        if args.quiet == False:
            lcds = [console(enabled=True)]

        if cfg['lcd_enabled']:
            if cfg['lcd_type'] == 'hd44780':
                lcds.append(hd44780(enabled=True,
                            rows=cfg['hdd44780_rows'],
                            cols=cfg['hdd44780_cols'],
                            d4=cfg['hdd44780_d4'],
                            d5=cfg['hdd44780_d5'],
                            d6=cfg['hdd44780_d6'],
                            d7=cfg['hdd44780_d7'],
                            en=cfg['hdd44780_en'],
                            rs=cfg['hdd44780_rs']))
            elif cfg['lcd_type'] == 'lcdproc':
                logging.warning('LCDProc not currently supported.')

        if cfg['hidkey_enabled']:
            lcds.append(hidkey(enabled=True,
                               device=cfg['hidkey_device']))

        wordlist = loadwordlist(cfg['pwd_dict'], cfg['pwd_minlength'], cfg['pwd_maxlength'])

        if args.once:
            outputpasswords(genpasswords(wordlist=wordlist,
                                         rng=rng,
                                         cfg=cfg),
                            lcds)
        elif cfg['button_enabled']:
            button = cmdbutton(cfg, lcds, wordlist, rng)
            button.run()
            while True:
                time.sleep(1)
            
    finally:
        g_run_threads = False
        try:
            for l in lcds:
                l.close()
        except:
            pass
        
