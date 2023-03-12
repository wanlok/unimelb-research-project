from utils import csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    files_csv_file_path = 'files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])

    row_dict = dict()

    for row in row_dict:
        key = f'{row[0]} {row[1]}'
        if key in row_dict:
            row_dict[key] = row_dict[key] + 1
        else:
            row_dict[key] = 1

    for key in row_dict:
        if row_dict[key] > 1:
            print(key)
