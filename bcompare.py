import subprocess
import sys

from utils import csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    repo = sys.argv[1]
    sha = sys.argv[2]
    file_directory = 'C:\\Files\\Projects\\unimelb-research-project'
    csv_file_path = '_'.join(repo.split('/'))
    csv_file_path = f'{file_directory}\\content\\{csv_file_path}.csv'
    csv_reader = csv_reader(csv_file_path)
    left_file_path = f'left.txt'
    right_file_path = f'right.txt'
    for row in csv_reader:
        if sha == row[2]:
            with open(left_file_path, 'w', encoding='utf-8') as f:
                f.write(row[4])
            with open(right_file_path, 'w', encoding='utf-8') as f:
                f.write(row[5])
            path = 'C:\\Program Files\\Beyond Compare 4\\BCompare.exe'
            subprocess.call([path, left_file_path, right_file_path])
            break
