import re
import sys

from utils import csv_reader, sort_by_descending_values


def get_url_strings(row):
    return list(set(map(lambda x: re.sub(r'URL:|MISC:|CONFIRM:', '', x).strip(), filter(lambda x: domain_name in x.lower(), row[3].split('|')))))


if __name__ == '__main__':
    path = 'C:\\Files\Projects\\allitems.csv'
    domain_name = 'https://github.com/'
    if sys.argv[1] == 'list':
        i = 0
        for row in csv_reader(path, encoding='latin-1'):
            if domain_name in row[3].lower():
                url_strings = get_url_strings(row)
                date_strings = re.findall(r'\d+', row[4])
                if len(date_strings) > 0:
                    if sys.argv[2].lower() in ' '.join(url_strings).lower():
                        i = i + 1
                        print(f'{i} {row[0]} {date_strings[0]} {url_strings}')
    elif sys.argv[1] == 'count':
        count_dict = dict()
        for row in csv_reader(path, encoding='latin-1'):
            if domain_name in row[3].lower():
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
            if i < int(sys.argv[2]):
                print(f'{count_dict[repo]} {repo}')
            i = i + 1
    elif sys.argv[1] == 'a':
        for row in csv_reader(path, encoding='latin-1'):
            print(get_url_strings(row))
