import re
import sys

from utils import csv_reader, sort_by_descending_values, csv_writer, prepare_csv_file

path = 'C:\\Files\Projects\\allitems.csv'
domain_name = 'https://github.com/'


def get_url_strings(row):
    return list(set(filter(lambda x: x.lower().startswith(domain_name), map(lambda x: re.sub(r'URL:|MISC:|CONFIRM:', '', x).strip(), row[3].split('|')))))


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        i = 0
        for row in csv_reader(path, encoding='latin-1'):
            url_strings = get_url_strings(row)
            date_strings = re.findall(r'\d+', row[4])
            exists = False
            for url_string in url_strings:
                if sys.argv[2].lower() in url_string.lower():
                    exists = True
                    break
            if exists and len(date_strings) > 0:
                i = i + 1
                print(f'{i} {row[0]} {date_strings[0]} {url_strings}')
    elif sys.argv[1] == 'count':
        if len(sys.argv) > 3:
            repo_csv_file_path = sys.argv[3]
            repo_csv_writer = csv_writer(repo_csv_file_path, mode='w')
            repo_csv_reader = csv_reader(repo_csv_file_path)
            repo_csv_rows = prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
        count_dict = dict()
        for row in csv_reader(path, encoding='latin-1'):
            repos = set()
            for url_string in get_url_strings(row):
                slices = re.sub(domain_name, '', url_string).split('/')
                if len(slices) > 1:
                    repos.add(f'{slices[0]}/{slices[1]}')
            for repo in repos:
                if repo in count_dict:
                    count_dict[repo] = count_dict[repo] + 1
                else:
                    count_dict[repo] = 1
        i = 0
        for repo in sort_by_descending_values(count_dict):
            i = i + 1
            if len(sys.argv) < 3 or i <= int(sys.argv[2]):
                print(f'{i} {repo} {count_dict[repo]}')
                if len(sys.argv) > 3:
                    repo_csv_writer.writerow([repo])
    elif sys.argv[1] == 'a':
        for row in csv_reader(path, encoding='latin-1'):
            print(get_url_strings(row))
