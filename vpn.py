from subprocess import call

from nordvpn_switcher import initialize_VPN, rotate_VPN

if __name__ == '__main__':
    initialize_VPN(save=1, area_input=['singapore', 'hong kong'])
    while True:
        rotate_VPN()
        call(['py', 'crawler_6.py'])