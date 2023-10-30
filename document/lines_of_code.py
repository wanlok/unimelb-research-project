import os
import shutil
import subprocess

from utils import repos

cloc_directory_path = 'C:\\Files\\Projects\\cloc\\'
temp_directory_path = 'C:\\Files\\Projects\\cloc\\temp-linecount-repo'
os.chdir(cloc_directory_path)


def cloc_git(repo):
    if os.path.exists(temp_directory_path):
        shutil.rmtree(temp_directory_path)
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    file_path = f'{cloc_directory_path}{file_name}'
    if not os.path.exists(file_path):
        print(f'{repo} {file_path}')
        p = subprocess.Popen(['cloc-git', repo], stdout=subprocess.PIPE, shell=True)
        content, _ = p.communicate()
        with open(file_path, 'w') as f:
            f.write(content.decode())


def get_counts(repo):
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    file_path = f'{cloc_directory_path}{file_name}'
    lines_of_code = None
    if os.path.exists(file_path):
        file = open(file_path, 'r')
        for line in file.readlines():
            if 'SUM:' in line:
                lines_of_code = int(list(filter(lambda x: len(x) > 0, line.strip().split(' ')))[1:][3])
                break
    if lines_of_code is None:
        print(f'{repo},')
    else:
        print(f'{repo},{lines_of_code}')


if __name__ == '__main__':
    repos(get_counts)