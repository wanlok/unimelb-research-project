import sys

from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_csv_start_index, get_content

if __name__ == '__main__':
    _, repo, path = sys.argv
    file_path = repo.replace('/', '_')
    file_path = f'./content/{file_path}.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance'])
    data_1, error_1 = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
    if data_1 is not None:
        for i in range(len(data_1)):
            sha = data_1[i]['sha']
            data_2, error_2 = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
            if data_2 is not None:
                date_time = parser.parse(data_2['commit']['committer']['date'])
                for file in data_2['files']:
                    if file["filename"] == path:
                        content = get_content(file['raw_url'])
                        content = BeautifulSoup(eval(f'{content}').decode('utf-8'), features='lxml').get_text()
                        row = [repo, path, sha, date_time, content]
                        if row not in rows:
                            length = len(rows)
                            index = length
                            for j in range(length):
                                if date_time < rows[j][3]:
                                    index = j
                                    break
                            rows.insert(index, row)
    previous_content = ''
    for i in range(len(rows)):
        repo, path, sha, date_time, content = rows[i]
        writer.writerow([repo, path, sha, date_time, previous_content, content, distance(previous_content, content)])
        previous_content = content
