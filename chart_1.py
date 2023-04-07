import os
from datetime import datetime

import nvdcve
import repository
from chart import plot, scatter_plot
from security_md import get_date_statistics
from utils import csv_reader, get_start_and_end_date_string_before_date_minus_days

markdown_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'
chart_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\1\\'


def prepare_dataset(file_path):
    x = []
    y = []
    number_of_rows = 0
    date_dict = dict()
    for row in csv_reader(file_path):
        if row != repository.csv_header:
            sha = row[2]
            date = int(row[3][:10].replace('-', ''))
            if date in date_dict:
                date_dict[date].append(sha)
            else:
                date_dict[date] = [sha]
            number_of_rows = number_of_rows + 1
    previous_date = 0
    if len(date_dict) > 0:
        # cve_list = cve.dummy_list(repo)
        cve_list = nvdcve.get_list(repo)
        for date in date_dict:
            x.append(f'{date}')
            y.append(len([x for x in cve_list if previous_date < int(x[1]) < date]))
            previous_date = date
    return x, y, date_dict, number_of_rows


def append_html(writer, number_of_rows, date_dict, file_name):
    writer.write(f'<h3>{repo} ({number_of_rows})</h3>')
    writer.write(f'<div>{date_dict}</div>')
    writer.write(f'<a href=\"../../data/securities/{file_name}.csv\">CSV</a>')
    writer.write(f'<img src="{file_name}.png" />')
    writer.write(f'<hr />')


if __name__ == '__main__':
    number_of_days_before = 100
    styles = 'img {display: block; height: 480pt;} a {display: block;}'
    # writer = get_writer(f'{chart_path}index.html')
    # writer.write(f'<html><head><style>{styles}</style></head><body>')
    n = 99999
    x_title = "SECURITY.md Update Dates (Number of Updates)"
    y_title = f'Number of CVEs {number_of_days_before} Days Before'
    x_all_values = []
    y_all_values = []
    for repo in repository.get_list(200):
        slices = repo.split('/')
        file_name = '_'.join(slices)
        file_path = f'{markdown_path}{file_name}.csv'
        if os.path.exists(file_path):
            print(repo)
            x_values = []
            y_values = []
            date_list, date_dict = get_date_statistics(file_path)
            cve_list = nvdcve.get_list(repo)
            for date in date_list:
                start_date, end_date = get_start_and_end_date_string_before_date_minus_days(datetime.strptime(date, '%Y%m%d'), number_of_days_before, '%Y%m%d')
                number_of_security_md_commits = date_dict[date]
                x_values.append(f'{date} ({number_of_security_md_commits})')
                x_all_values.append(number_of_security_md_commits)
                y_values.append(len([x for x in cve_list if int(start_date) < int(x[1]) < int(end_date)]))
            y_all_values.extend(y_values)

            # x_values, y_values, date_dict, number_of_rows = prepare_dataset(file_path)
            # if len(x_values) == len(y_values) and len(x_values) > 0:
            #     print(repo)
            #     append_html(writer, number_of_rows, date_dict, file_name)
            plot(repo, x_values, y_values, x_title, y_title, f'{chart_path}{file_name}.png')
            #     n = n - 1
            #     if n == 0:
            #         break
    scatter_plot(x_all_values, y_all_values, f'{chart_path}distribution.png')
    # writer.write('</body></html>')
