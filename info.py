import glob
import re
from math import floor, ceil

import langid
import numpy as np
import pandas as pd

import cve
from utils import csv_reader, csv_writer, prepare_csv_file

import matplotlib.pyplot as plt


def plot(title, x, y):
    font_name = 'Times New Roman'
    font = {'fontname': font_name}
    fig = plt.figure()
    fig.set_size_inches(len(x) * 2, 8)
    plt.bar(x, y, color='black', width=0.24)
    plt.xticks(rotation=45, fontname=font_name)
    plt.xlabel('SECURITY.md Update Dates', fontdict=font, labelpad=24)
    plt.yticks(range(floor(min(y)), ceil(max(y)) + 1, 50), fontname=font_name)
    plt.ylabel('Number of CVEs Before Updates', fontdict=font, labelpad=24)
    plt.title(title, fontdict=font, pad=24)
    ax = plt.gca()
    for i in range(len(y)):
        rect = ax.patches[i]
        ax.text(rect.get_x() + rect.get_width() / 2, y[i], f'{y[i]}\n', ha='center', fontdict=font)
    plt.savefig(f'images/{name}.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    # content_csv_file_path = 'content.csv'
    # content_csv_reader = csv_reader(content_csv_file_path)
    info_file_path = 'info.csv'
    info_writer = csv_writer(info_file_path, mode='w')
    info_reader = csv_reader(info_file_path)
    info_rows = prepare_csv_file(info_reader, info_writer, ['repo', 'file_from_parent'])
    # i = 0
    # for row in content_csv_reader:
    #     if i > 0:
    #         content = eval(row[2]).decode('utf-8')
    #         headings = re.findall(r'[b\'|b\"|\\n]#+ *(.*?) *\\n', row[2])
    #         cve_count = content.lower().count('cve')
    #         language = langid.classify(content)[0].upper()
    #         content_info_csv_writer.writerow([row[0], row[1], len(headings), language, cve_count])
    #     i = i + 1
    repo_file_path = 'repo.csv'
    repo_writer = csv_writer(repo_file_path)
    repo_reader = csv_reader(repo_file_path)
    repo_rows = prepare_csv_file(repo_reader, repo_writer, ['repo'])
    directory = ''.join(glob.glob('content/*'))
    n = 9999
    for i in range(len(repo_rows)):
        repo = repo_rows[i][0]
        slices = repo.split('/')
        name = '_'.join(slices)
        file_name = f'{name}.csv'
        dates = []
        counts = []
        if file_name in directory:
            content_file_path = f'content/{file_name}'
            content_writer = csv_writer(content_file_path)
            content_reader = csv_reader(content_file_path)
            content_rows = prepare_csv_file(content_reader, content_writer, ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance'])
            number_of_rows = len(content_rows)
            date_dict = dict()
            for j in range(1, number_of_rows):
                date = int(content_rows[j][3][:10].replace('-', ''))
                if date in date_dict:
                    date_dict[date] = date_dict[date] + 1
                else:
                    date_dict[date] = 1
            previous_date = 0
            if len(date_dict) > 0:
                cve_list = cve.dummy_list(repo)
                for date in date_dict:
                    dates.append(f'{date}')
                    counts.append(len([x for x in cve_list if previous_date < x[1] < date]))
                    previous_date = date
                print(f'<h3>{i}. {repo} ({number_of_rows - 1})</h3>')
                print(f'<div>{date_dict}</div>')
                print(f'<a href=\"../content/{name}.csv\">CSV</a>')
                print(f'<img src="{name}.png" />')
                print(f'<hr />')
                plot(repo, dates, counts)
                n = n - 1
                if n == 0:
                    break
