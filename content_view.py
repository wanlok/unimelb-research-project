from bs4 import BeautifulSoup

from utils import csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    content_file_path = 'content.csv'
    content_writer = csv_writer(content_file_path)
    content_reader = csv_reader(content_file_path)
    content_rows = prepare_csv_file(content_reader, content_writer, ['repo', 'path', 'content'])
    content_view_file_path = 'content_view.csv'
    content_view_writer = csv_writer(content_view_file_path)
    content_view_reader = csv_reader(content_view_file_path)
    content_view_rows = prepare_csv_file(content_view_reader, content_view_writer, ['repo', 'path', 'content'])
    for i in range(1, len(content_rows)):
        repo = content_rows[i][0]
        path = content_rows[i][1]
        content = BeautifulSoup(eval(content_rows[i][2]).decode('utf-8'), features='lxml').get_text()
        content_view_writer.writerow([repo, path, content])
