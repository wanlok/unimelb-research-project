import csv


def contain_folder(name, row):
    file_names = list(map(lambda s: s.strip('\''), row[1].strip('][').split(', ')))
    return len([file_name for file_name in file_names if file_name == name]) > 0


if __name__ == '__main__':
    csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repositories.csv'
    read_file = open(csv_file_path)
    reader = csv.reader(read_file, delimiter=',')
    old_repository_names = set()
    for row in reader:
        if contain_folder('docs', row):
            print(row[0])

