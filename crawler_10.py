import sys

from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_csv_start_index, get_content

if __name__ == '__main__':
    input_file_path = 'files.csv'
    input_writer = csv_writer(input_file_path)
    input_reader = csv_reader(input_file_path)
    input_rows = prepare_csv_file(input_reader, input_writer, ['repo', 'path', 'url'])
    output_file_path = sys.argv[3]
    output_writer = csv_writer(output_file_path, mode='w')
    output_reader = csv_reader(output_file_path)
    output_rows = prepare_csv_file(output_reader, output_writer, ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance'])
    for row in input_rows:
        repo, path, _ = row
        if repo == sys.argv[1] and path == sys.argv[2]:
            data_1, error_1 = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
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
                            if row not in output_rows:
                                length = len(output_rows)
                                index = length
                                for j in range(length):
                                    if date_time < output_rows[j][3]:
                                        index = j
                                        break
                                output_rows.insert(index, row)
    previous_content = ''
    for i in range(len(output_rows)):
        repo, path, sha, date_time, content = output_rows[i]
        output_writer.writerow([repo, path, sha, date_time, previous_content, content, distance(previous_content, content)])
        previous_content = content
