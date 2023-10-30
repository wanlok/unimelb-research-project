from utils import repos


def pr(key, my_dict):
    if key in my_dict:
        value = my_dict[key]
    else:
        value = 0
    return value


def dummy(repo):
    my_dict = dict()
    directory_pathh = 'C:\\Files\\Projects\\Pull Requests\\'
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    with open(f'{directory_pathh}{file_name}') as f:
        lines = f.readlines()
        if len(lines) > 0:
            my_list = list(map(lambda x: x['node']['createdAt'], eval(lines[0])))
            for item in my_list:
                key = item[:4]
                if key in my_dict:
                    my_dict[key] = my_dict[key] + 1
                else:
                    my_dict[key] = 1
    aaa = [
        pr('2018', my_dict),
        pr('2019', my_dict),
        pr('2020', my_dict),
        pr('2021', my_dict),
        pr('2022', my_dict),
        pr('2023', my_dict),
    ]
    aaa = ','.join(list(map(lambda x: f'{x}', aaa)))
    print(f'"{repo}",{aaa}')


if __name__ == '__main__':
    print('Hello World')
    repos(dummy)
    # dummy('dovecot/core')