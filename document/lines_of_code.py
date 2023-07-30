import os
import shutil
import subprocess

cloc_directory_path = 'C:\\Files\\Projects\\cloc\\'
temp_directory_path = 'C:\\Files\\Projects\\cloc\\temp-linecount-repo'
os.chdir(cloc_directory_path)


from utils import repos


def do_something(repo):
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


if __name__ == '__main__':
    repos(do_something)
    # do_something('wanlok/dummy')