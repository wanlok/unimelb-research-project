import sys

import commit_history

if __name__ == '__main__':
    slices = sys.argv[1].split('/')
    repos = [sys.argv[1], f'{slices[0]}/.github']
    if len(sys.argv) > 2 and sys.argv[2] == 'l':
        paths = [['security.md', '.github/security.md', 'docs/security.md'], ['security.md']]
    else:
        paths = [['SECURITY.md', '.github/SECURITY.md', 'docs/SECURITY.md'], ['SECURITY.md']]
    file_path = '_'.join(slices)
    file_path = f'./content/{file_path}.csv'
    commit_history.download(repos, paths, file_path)
