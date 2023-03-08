import re

import langid

from utils import csv_reader, csv_writer, prepare_csv_file

if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)
    info_csv_file_path = 'info.csv'
    info_csv_writer = csv_writer(info_csv_file_path, mode='w')
    info_csv_reader = csv_reader(info_csv_file_path)
    info_csv_rows = prepare_csv_file(info_csv_reader, info_csv_writer, ['repo', 'path', 'number_of_headings', 'language'])
    i = 0
    for row in content_csv_reader:
        if i > 0:
            headings = re.findall(r'[b\'|b\"|\\n]#+ *(.*?) *\\n', row[2])
            language = langid.classify(eval(row[2]).decode('utf-8'))[0].upper()
            info_csv_writer.writerow([row[0], row[1], len(headings), language])
        i = i + 1
