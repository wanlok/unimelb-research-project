import sys
from html.parser import HTMLParser

from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    file_content_mapping_csv_file_path = 'file_content_mapping.csv'
    file_content_mapping_csv_writer = csv_writer(file_content_mapping_csv_file_path)
    file_content_mapping_csv_reader = csv_reader(file_content_mapping_csv_file_path)
    file_content_mapping_csv_rows = prepare_csv_file(file_content_mapping_csv_reader, file_content_mapping_csv_writer, ['repo', 'path', 'date_time', 'content'])
    history_csv_file_path = 'history.csv'
    history_csv_writer = csv_writer(history_csv_file_path, mode='w')
    history_csv_reader = csv_reader(history_csv_file_path)
    history_csv_rows = prepare_csv_file(history_csv_reader, history_csv_writer, ['repo', 'path', 'date_time', 'previous_content', 'content', 'levenshtein_distance'])
    targets = []
    for i in range(1, len(file_content_mapping_csv_rows)):
        row = file_content_mapping_csv_rows[i]
        repo = row[0]
        if sys.argv[1].lower() in repo.lower():
            path = row[1]
            date_time = parser.parse(row[2])
            content = BeautifulSoup(eval(row[3]).decode('utf-8'), features='lxml').get_text()
            length = len(targets)
            index = length
            for j in range(length):
                if date_time < targets[j][2]:
                    index = j
                    break
            targets.insert(index, [repo, path, date_time, content])
    previous_content = ''
    for i in range(len(targets)):
        repo, path, date_time, content = targets[i]
        history_csv_writer.writerow([repo, path, date_time, previous_content, content, distance(previous_content, content)])
        previous_content = content

