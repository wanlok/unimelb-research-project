import sys

from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_content

if __name__ == '__main__':
    slices = sys.argv[1].split('/')
    repos = [sys.argv[1], f'{slices[0]}/.github']
    paths = [['SECURITY.md', '.github/SECURITY.md', 'docs/SECURITY.md'], ['SECURITY.md']]
    # paths = [['security.md', '.github/security.md', 'docs/security.md'], ['security.md']]
    file_path = '_'.join(slices)
    file_path = f'./content/{file_path}.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance', 'bcompare'])
    valid = False
    for i in range(len(repos)):
        repo = repos[i]
        for path in paths[i]:
            data_1, error_1 = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
            if data_1 is not None:
                valid = len(data_1) > 0
                for j in range(len(data_1)):
                    sha = data_1[j]['sha']
                    data_2, error_2 = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
                    if data_2 is not None:
                        date_time = parser.parse(data_2['commit']['committer']['date'])
                        for file in data_2['files']:
                            if file["filename"] == path:
                                content = get_content(file['raw_url'])
                                content = BeautifulSoup(eval(f'{content}').decode('utf-8'), features='lxml').get_text()
                                row = [repo, path, sha, date_time, content]
                                if row not in rows:
                                    index = len(rows)
                                    for k in range(len(rows)):
                                        if date_time < rows[k][3]:
                                            index = k
                                            break
                                    rows.insert(index, row)
            if valid:
                break
        if valid:
            break
    previous_content = ''
    for j in range(len(rows)):
        repo, path, sha, date_time, content = rows[j]
        writer.writerow([repo, path, sha, date_time, previous_content, content, distance(previous_content, content), f'b {repos[0]} {sha}'])
        previous_content = content
