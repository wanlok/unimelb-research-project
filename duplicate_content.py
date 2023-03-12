import time

from utils import get_json, csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    # json_array = get_json('https://api.github.com/repos/wanlok/unimelb-research-project/commits?path=SECURITY.md')
    # for json_object in json_array:
    #     commit = json_object['commit']
    #     date = commit['committer']['date']
    #     message = commit['message']
    #     print(f'{date} {message}')

    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)
    content_csv_writer = csv_writer(content_csv_file_path)
    content_csv_rows = prepare_csv_file(content_csv_reader, content_csv_writer, ['repo', 'path', 'content'])

    row_dict = dict()

    for row in content_csv_rows:
        key = f'{row[0]} {row[1]}'
        if key in row_dict:
            row_dict[key] = row_dict[key] + 1
        else:
            row_dict[key] = 1

    for key in row_dict:
        if row_dict[key] > 1:
            print(key)
