import csv
import time

from nordvpn_switcher import initialize_VPN, rotate_VPN

from utils import csv_writer, csv_reader, read_csv_file

if __name__ == '__main__':
    time_limit = 0.5

    initialize_VPN(save=1, area_input=['malaysia', 'singapore', 'vietnam'])

    for i in range(3):
        rotate_VPN()
        print('\nDo whatever you want here (e.g.scraping). Pausing for 10 seconds...\n')
        time.sleep(10)