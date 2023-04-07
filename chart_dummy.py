import repository

security_md_directory_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'

if __name__ == '__main__':
    print('hihi')
    for repo in repository.get_list(10):
        print(repo)