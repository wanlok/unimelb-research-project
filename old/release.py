from datetime import datetime

from Levenshtein import distance

import repository
from utils import get_file_json, csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    repos = repository.get_list(200)
    for repo in repos:
        file_name = '_'.join(repo.split('/'))
        file_path = f'C:\\Files\\Projects\\unimelb-research-project-java\\data\\releases\\{file_name}.json'
        releases = get_file_json(file_path)
        rows = []
        previous_content = ''
        contain_cve = False
        for i in reversed(range(len(releases))):
            release = releases[i]
            date_time = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ')
            index = len(rows)
            for j in range(len(rows)):
                if date_time < rows[j][0]:
                    index = j
                    break
            content = release['body']
            if content is not None:
                rows.insert(index, [date_time, previous_content, content, distance(previous_content, content), ''])
                previous_content = content
                if 'cve' in content.lower():
                    contain_cve = True
        if contain_cve:
            file_path = f'data\\releases\\{file_name}.csv'
            writer = csv_writer(file_path, mode='w')
            reader = csv_reader(file_path)
            prepare_csv_file(reader, writer, ['date_time', 'previous_content', 'content', 'levenshtein_distance', 'bcompare'])
            for row in rows:
                writer.writerow(row)