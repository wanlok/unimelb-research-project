import re

from utils import csv_reader

if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)

    dict = dict()
    for row in content_csv_reader:
        key = f'{row[0]} {row[1]}'
        if key in dict:
            dict[key] = dict[key] + 1
        else:
            dict[key] = 1
    for a in dict:
        if dict[a] > 1:
            print(f'{a} {dict[a]}')



    # i = 9999
    # titles = set()
    # list
    # for row in content_csv_reader:
    #     lll = re.findall(r'#+ *(.*?)\\n', row[2])
    #     # print(f'{row[0]} {row[1]} {lll}')
    #     titles.update(lll)
    # print(titles)