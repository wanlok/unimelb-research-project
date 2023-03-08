from urllib.parse import quote

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_content, get_csv_start_index


if __name__ == '__main__':
    files_csv_file_path = 'files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    content_csv_file_path = 'content.csv'
    content_csv_writer = csv_writer(content_csv_file_path)
    content_csv_reader = csv_reader(content_csv_file_path)
    content_csv_rows = prepare_csv_file(content_csv_reader, content_csv_writer, ['repo', 'path', 'content'])
    start_index = get_csv_start_index(files_csv_rows, content_csv_rows, 2)
    print(f'{start_index} {len(files_csv_rows)}')
    while start_index < len(files_csv_rows):
        repo = quote(files_csv_rows[start_index][0])
        path = quote(files_csv_rows[start_index][1])
        content = get_json(f'https://api.github.com/repos/{repo}/contents/{path}')
        if content is not None:
            download_url = content['download_url']
            row = [repo, path, get_content(download_url)]
            if row not in content_csv_rows:
                content_csv_writer.writerow(row)
                content_csv_rows.append(row)
        start_index = start_index + 1
