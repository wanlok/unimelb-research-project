import subprocess
import sys

from utils import csv_reader

exit_command = 'taskkill /F /IM BCompare.exe'

program_path = 'C:\\Program Files\\Beyond Compare 4\\BCompare.exe'
left_path = 'C:\\Files\\Projects\\unimelb-research-project\\left.txt'
right_path = 'C:\\Files\\Projects\\unimelb-research-project\\right.txt'

directory_paths = [
    # 'C:\\Files\\Projects\\unimelb-research-project\\content\\',
    'C:\\Files\\Projects\\unimelb-research-project\\data\\commits\\requirements_txt\\',
    'C:\\Files\\Projects\\unimelb-research-project\\data\\commits\\composer_json\\',
    'C:\\Files\\Projects\\unimelb-research-project\\data\\commits\\package_json\\',
    'C:\\Files\\Projects\\unimelb-research-project\\data\\securities\\',
    'C:\\Files\\Projects\\unimelb-research-project\\data\\document\\'
]


if __name__ == '__main__':
    repo = sys.argv[1]
    sha = sys.argv[2]
    file_name = '_'.join(repo.split('/'))
    for directory_path in directory_paths:
        file_path = f'{directory_path}{file_name}.csv'
        try:
            for row in csv_reader(file_path):
                if sha == row[2]:
                    subprocess.run(exit_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    with open(left_path, 'w', encoding='utf-8') as f:
                        f.write(row[4])
                    with open(right_path, 'w', encoding='utf-8') as f:
                        f.write(row[5])
                    print(f'FILE PATH            : {file_path}')
                    print(f'REPO                 : {row[0]}')
                    print(f'PATH                 : {row[1]}')
                    print(f'SHA                  : {row[2]}')
                    print(f'DATE TIME            : {row[3]}')
                    print(f'LEVENSHTEIN DISTANCE : {row[6]}')
                    subprocess.call([program_path, left_path, right_path])
                    break
        except FileNotFoundError as e:
            pass
