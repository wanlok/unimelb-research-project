import os
from datetime import datetime

import repository
from utils import csv_reader

markdown_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'
chart_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\1\\'


if __name__ == '__main__':
    dummy_dict = dict()
    for repo in repository.get_list():
        slices = repo.split('/')
        file_name = '_'.join(slices)
        file_path = f'{markdown_path}{file_name}.csv'
        if os.path.exists(file_path):
            for row in csv_reader(file_path):
                try:
                    key = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m')
                    if key in dummy_dict:
                        dummy_list = dummy_dict[key]
                    else:
                        dummy_list = []
                        dummy_dict[key] = dummy_list
                    if repo.lower() not in map(lambda x: x.lower(), dummy_list):
                        dummy_list.append(repo)
                except ValueError:
                    pass
    dummy = sorted(dummy_dict.items(), key=lambda x: len(x[1]), reverse=True)
    for d in dummy:
        print(d)