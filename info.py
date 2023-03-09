import re

import langid

from utils import csv_reader, csv_writer, prepare_csv_file

if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)
    content_info_csv_file_path = 'info.csv'
    content_info_csv_writer = csv_writer(content_info_csv_file_path, mode='w')
    content_info_csv_reader = csv_reader(content_info_csv_file_path)
    content_info_csv_rows = prepare_csv_file(content_info_csv_reader, content_info_csv_writer, ['repo', 'path', 'number_of_headings', 'language', 'cve_count'])
    i = 0
    for row in content_csv_reader:
        if i > 0:
            content = eval(row[2]).decode('utf-8')
            headings = re.findall(r'[b\'|b\"|\\n]#+ *(.*?) *\\n', row[2])
            cve_count = content.lower().count('cve')
            language = langid.classify(content)[0].upper()
            content_info_csv_writer.writerow([row[0], row[1], len(headings), language, cve_count])
        i = i + 1
