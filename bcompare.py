import subprocess
import sys

from utils import csv_reader

left_file_path = 'left.txt'
right_file_path = 'right.txt'

directory_paths = [
    'C:\\Files\\Projects\\unimelb-research-project\\content\\',
    'C:\\Files\\Projects\\unimelb-research-project\\commit_histories\\requirements_txt\\'
]


if __name__ == '__main__':
    repo = sys.argv[1]
    sha = sys.argv[2]
    file_name = '_'.join(repo.split('/'))
    for directory_path in directory_paths:
        file_path = f'{directory_path}{file_name}.csv'
        for row in csv_reader(file_path):
            if sha == row[2]:
                with open(left_file_path, 'w', encoding='utf-8') as f:
                    f.write(row[4])
                with open(right_file_path, 'w', encoding='utf-8') as f:
                    f.write(row[5])
                print(f'FILE PATH:           : {file_path}')
                print(f'REPO                 : {row[0]}')
                print(f'PATH                 : {row[1]}')
                print(f'SHA                  : {row[2]}')
                print(f'DATE TIME            : {row[3]}')
                print(f'LEVENSHTEIN DISTANCE : {row[6]}')
                path = 'C:\\Program Files\\Beyond Compare 4\\BCompare.exe'
                subprocess.call([path, left_file_path, right_file_path])
                break
