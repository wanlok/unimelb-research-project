import csv


if __name__ == '__main__':
    csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repositories.csv'
    read_file = open(csv_file_path)
    reader = csv.reader(read_file, delimiter=',')
    old_repository_names = set()
    for row in reader:
        files = list(map(lambda s: s.strip('\''), row[2].strip('][').split(', ')))
        if 'doc' in files:
            print(row[0])

