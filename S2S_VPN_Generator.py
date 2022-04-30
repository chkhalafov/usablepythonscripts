"""
Site-to-Site config generator
Author Chingiz V. Khalafov
Company: Rabitabank OJSC
"""

from pip._vendor.distlib.compat import raw_input
import string
import random

LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = string.punctuation
SPEC_SYMBOLS = "@!#"

PARTNER_IP = raw_input("Enter partners Public IP: ")
PARTNER = raw_input("Enter partners friendly name: ").upper()
PRE_SHARED_KEY = raw_input("Enter pre-shared key: ")
MAP_IP = raw_input("Enter local map IP: ")
LOCAL_HOST_IP = raw_input("Enter Local host IP: ")
REMOTE_HOST_IP = raw_input("Enter Remote host IP: ")
SEQ_NUMBER = raw_input("Enter crypto map seq number: ")
CONNECT_TO_US = raw_input("Does partner connect to our environment? Yes/No: ").upper()


def psk_generator(length):
    # create alphanumerical from string constants
    printable = f'{LETTERS}{NUMBERS}{SPEC_SYMBOLS}'

    # convert printable from string to list and shuffle
    printable = list(printable)
    random.shuffle(printable)

    # generate random password and convert to string
    random_password = random.choices(printable, k=length)
    random_password = ''.join(random_password)
    return random_password


if PRE_SHARED_KEY == "":
    PRE_SHARED_KEY = psk_generator(14)

config = '''
======== Site-to-Site VPN Config is Ready ========
object-group network LOCAL-MAP-{PARTNER}
network-object host {MAP_IP}
object-group network LAN-VPN-{PARTNER}
network-object host {LOCAL_HOST_IP}
object-group network REMOTE-VPN-{PARTNER}
network-object host {REMOTE_HOST_IP}

access-list VPN-TRAFFIC-{PARTNER} permit ip object-group LOCAL-MAP-{PARTNER} REMOTE-VPN-{PARTNER}

group-policy {PARTNER_IP} internal
tunnel-group {PARTNER_IP} type ipsec-l2l
tunnel-group {PARTNER_IP} general-attributes
default-group-policy {PARTNER_IP}
tunnel-group {PARTNER_IP} ipsec-attributes
ikev1 pre-shared-key {PRE_SHARED_KEY}

crypto ipsec ikev1 transform-set {PARTNER}_TS esp-aes-256 esp-sha-hmac

crypto map rb_vpn_map {SEQ_NUMBER} match address VPN-TRAFFIC-{PARTNER}
crypto map rb_vpn_map {SEQ_NUMBER} set pfs
crypto map rb_vpn_map {SEQ_NUMBER} set peer {PARTNER_IP}
crypto map rb_vpn_map {SEQ_NUMBER} set ikev1 transform-set {PARTNER}_TS
crypto map rb_vpn_map {SEQ_NUMBER} set security-association lifetime seconds 3600

nat (privatelan,publiclan) source static LAN-VPN-{PARTNER} LOCAL-MAP-{PARTNER} destination static REMOTE-VPN-{PARTNER} REMOTE-VPN-{PARTNER} unidirectional
'''.format(PARTNER=PARTNER, MAP_IP=MAP_IP, LOCAL_HOST_IP=LOCAL_HOST_IP, REMOTE_HOST_IP=REMOTE_HOST_IP,
           PARTNER_IP=PARTNER_IP, PRE_SHARED_KEY=PRE_SHARED_KEY, SEQ_NUMBER=SEQ_NUMBER)

print(config)

if CONNECT_TO_US == "YES":
    print('''
            nat (publiclan,privatelan) source static REMOTE-VPN-{PARTNER} REMOTE-VPN-{PARTNER} destination static LOCAL-MAP-{PARTNER} LAN-VPN-{PARTNER}
            access-list VPN-FILTER- {PARTNER} permit ip object-group REMOTE-VPN- {PARTNER} LOCAL-MAP- {PARTNER}
            group-policy {PARTNER_IP} attributes
            vpn-filter value VPN-FILTER-{PARTNER}
            '''.format(PARTNER=PARTNER, PARTNER_IP=PARTNER_IP)
          )
