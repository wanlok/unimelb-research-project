import re

import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

from utils import csv_reader, csv_writer, prepare_csv_file, sort_by_descending_values

email_regex = r'[\w\.-]+@[\w\.-]+'
url_regex = r'https?://[^\s)]+(?!\s)'


def write_content_summary(writer, repo, path, section, emails, urls, number_of_code_blocks):
    number_of_emails = len(emails)
    number_of_urls = len(urls)
    number_of_code_blocks = int(number_of_code_blocks / 2)
    if number_of_emails > 0 or number_of_urls > 0 or number_of_code_blocks > 0:
        writer.writerow([repo, path, section, number_of_emails, number_of_urls, number_of_code_blocks])


def write_content_summary_word(writer, repo, path, section, count_dict):
    for key in count_dict:
        writer.writerow([repo, path, section, key, count_dict[key]])


def tokenize(line, count_dict):
    line = re.sub(email_regex, '', line)
    line = re.sub(url_regex, '', line)
    line = line.lower()
    line = re.sub('[^a-z]+', ' ', line)
    for key in nltk.word_tokenize(line):
        if len(key) > 1 and key not in stopwords.words("english"):
            if key in count_dict:
                count_dict[key] = count_dict[key] + 1
            else:
                count_dict[key] = 1


if __name__ == '__main__':
    content_file_path = 'content.csv'
    content_writer = csv_writer(content_file_path)
    content_reader = csv_reader(content_file_path)
    content_rows = prepare_csv_file(content_reader, content_writer, ['repo', 'path', 'content'])
    content_summary_file_path = 'content_summary.csv'
    content_summary_writer = csv_writer(content_summary_file_path, mode='w')
    content_summary_reader = csv_reader(content_summary_file_path)
    content_summary_rows = prepare_csv_file(content_summary_reader, content_summary_writer, ['repo', 'path', 'section', 'number_of_emails', 'number_of_urls', 'number_of_code_blocks'])
    content_summary_word_file_path = 'content_summary_word.csv'
    content_summary_word_writer = csv_writer(content_summary_word_file_path, mode='w')
    content_summary_word_reader = csv_reader(content_summary_word_file_path)
    content_summary_word_rows = prepare_csv_file(content_summary_word_reader, content_summary_word_writer, ['repo', 'path', 'section', 'word', 'count'])
    for i in range(1, len(content_rows)):
        row = content_rows[i]
        repo = row[0]
        path = row[1]
        content = BeautifulSoup(eval(row[2]).decode('utf-8'), features='lxml').get_text()
        section = ''
        emails = []
        urls = []
        number_of_code_blocks = 0
        count_dict = {}
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                write_content_summary(content_summary_writer, repo, path, section, emails, urls, number_of_code_blocks)
                write_content_summary_word(content_summary_word_writer, repo, path, section, count_dict)
                section = line.replace('#', '').strip()
                emails = []
                urls = []
                number_of_code_blocks = 0
                count_dict = {}
            emails.extend(re.findall(email_regex, line))
            urls.extend(re.findall(url_regex, line))
            number_of_code_blocks = number_of_code_blocks + line.count('```')
            tokenize(line, count_dict)
        write_content_summary(content_summary_writer, repo, path, section, emails, urls, number_of_code_blocks)
        write_content_summary_word(content_summary_word_writer, repo, path, section, count_dict)

