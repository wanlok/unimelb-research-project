import git_repository
from utils import get_json

if __name__ == '__main__':
    # repos = git_repository.get_list(1)
    repo = 'firefly-iii/firefly-iii'
    path = '.github/security.md'
    # for i in range(len(repos)):
    #     repo = repos[i]
    data_1, error_1 = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
    if data_1 is not None:
        print(data_1)