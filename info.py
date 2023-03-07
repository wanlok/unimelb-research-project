import re

from utils import csv_reader, csv_writer, prepare_csv_file

if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)
    info_csv_file_path = 'info.csv'
    info_csv_writer = csv_writer(info_csv_file_path)
    info_csv_reader = csv_reader(info_csv_file_path)
    info_csv_rows = prepare_csv_file(info_csv_reader, info_csv_writer, ['repo', 'path', 'number_of_headings'])
    i = 0
    for row in content_csv_reader:
        if i > 0:
            if row[1] == 'doc/development/fe_guide/security.md':
                headings = re.findall(r'[b\'|b\"|\\n]#+ *(.*?) *\\n', row[2])
                print(f'{row[0]} {headings}')
            # info_csv_writer.writerow([row[0], row[1], len(headings)])
        i = i + 1
