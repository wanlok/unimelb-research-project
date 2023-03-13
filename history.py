import sys

from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    file_content_mapping_csv_file_path = 'file_content_mapping.csv'
    file_content_mapping_csv_writer = csv_writer(file_content_mapping_csv_file_path)
    file_content_mapping_csv_reader = csv_reader(file_content_mapping_csv_file_path)
    file_content_mapping_csv_rows = prepare_csv_file(file_content_mapping_csv_reader, file_content_mapping_csv_writer, ['repo', 'path', 'date_time', 'content'])
    compare_csv_file_path = 'compare.csv'
    compare_csv_writer = csv_writer(compare_csv_file_path, mode='w')
    compare_csv_reader = csv_reader(compare_csv_file_path)
    compare_csv_rows = prepare_csv_file(compare_csv_reader, compare_csv_writer, ['date_time', 'content'])
    targets = []
    for row in file_content_mapping_csv_rows:
        if row[0] == 'glpi-project/glpi':
            date_time = parser.parse(row[2])
            length = len(targets)
            index = length
            for i in range(length):
                target_date_time = parser.parse(targets[i][2])
                if date_time < target_date_time:
                    index = i
                    break
            targets.insert(index, row)
    for row in targets:
        print(row)

    # for row in file_content_mapping_csv_rows:
    #     if row[0] == 'glpi-project/glpi':
    #         print(f'-------------------- {row[1]} {row[2]}')
    #         print(eval(row[3]).decode('utf-8'))