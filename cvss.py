from datetime import datetime, timedelta

import chart
import repository
import nvdcve
from utils import csv_writer, csv_reader, prepare_csv_file

rating_names = ['Low', 'Medium', 'High', 'Critical', 'None']
v2_legends = ['0.0 - 0.9', '1.0 - 1.9', '2.0 - 2.9', '3.0 - 3.9', '4.0 - 4.9', '5.0 - 5.9', '6.0 - 6.9', '7.0 - 7.9', '8.0 - 8.9', '9.0 - 10.0']
v3_legends = ['0.1 - 0.9', '1.0 - 1.9', '2.0 - 2.9', '3.0 - 3.9', '4.0 - 4.9', '5.0 - 5.9', '6.0 - 6.9', '7.0 - 7.9', '8.0 - 8.9', '9.0 - 10.0']
colors = ['#2B472B', '#407A52', '#8DB255', '#9FD4A3', 'yellow', '#FFEE75', '#FBE106', 'orange', '#F9690E', '#DC3023']


def get_v2_rating(score):
    rating = 'None'
    score = 0 if score is None or len(score) == 0 else float(score)
    if score >= 0.0 and score <= 3.9:
        rating = 'Low'
    elif score >= 4.0 and score <= 6.9:
        rating = 'Medium'
    elif score >= 7.0 and score <= 10.0:
        rating = 'High'
    return rating


def get_v3_rating(score):
    rating = 'None'
    score = 0 if score is None or len(score) == 0 else float(score)
    if score >= 0.1 and score <= 3.9:
        rating = 'Low'
    elif score >= 4.0 and score <= 6.9:
        rating = 'Medium'
    elif score >= 7.0 and score <= 8.9:
        rating = 'High'
    elif score >= 9.0 and score <= 10.0:
        rating = 'Critical'
    return rating


def increment_rating(list, name):
    i = rating_names.index(name)
    list[i] = list[i] + 1


def increment_number(list, num):
    if len(num) > 0:
        i = int(float(num))
        if i == len(list):
            i = i - 1
        list[i] = list[i] + 1


def rating(my_list):
    return ', '.join(list(map(lambda x: f'{rating_names[x[0]]}: {x[1]}', filter(lambda x: x[1] > 0, enumerate(my_list)))))


def number(my_list):
    return my_list


def generate_charts(repo, dates, yesterday_dates):
    # cve_list = nvdcve.get_list(repo)
    # date_dict = dict()
    # for cve in cve_list:
    #     date_dict[int(cve[1][:-2])] = 1
    # date_list = list(date_dict.keys())
    # date_list.sort()
    v2_i = []
    v2_e = []
    v3_i = []
    v3_e = []
    for date in yesterday_dates:
        cve_list = nvdcve.get_list(repo, date)
        v2_i_rating_list = [0, 0, 0, 0, 0]
        v2_i_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v2_e_rating_list = [0, 0, 0, 0, 0]
        v2_e_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v3_i_rating_list = [0, 0, 0, 0, 0]
        v3_i_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v3_e_rating_list = [0, 0, 0, 0, 0]
        v3_e_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for cve in cve_list:
            increment_rating(v2_i_rating_list, get_v2_rating(cve[2]))
            increment_number(v2_i_number_list, cve[2])
            increment_rating(v2_e_rating_list, get_v2_rating(cve[3]))
            increment_number(v2_e_number_list, cve[3])
            increment_rating(v3_i_rating_list, get_v3_rating(cve[4]))
            increment_number(v3_i_number_list, cve[4])
            increment_rating(v3_e_rating_list, get_v3_rating(cve[5]))
            increment_number(v3_e_number_list, cve[5])
        print(f'{date}')
        print(f'Version 2 Impact        : {v2_i_number_list} {rating(v2_i_rating_list)}')
        print(f'Version 2 Explotability : {v2_e_number_list} {rating(v2_e_rating_list)}')
        print(f'Version 3 Impact        : {v3_i_number_list} {rating(v3_i_rating_list)}')
        print(f'Version 3 Explotability : {v3_e_number_list} {rating(v3_e_rating_list)}')
        v2_i.append(v2_i_number_list)
        v2_e.append(v2_e_number_list)
        v3_i.append(v3_i_number_list)
        v3_e.append(v3_e_number_list)
    file_name = '_'.join(repo.split('/'))
    chart.plot2(f'{repo} - CVSS v2 Impact Score before SECURITY.md commits', dates, v2_i, v2_legends, colors, f'cvss/v2/impact/{file_name}.png')
    chart.plot2(f'{repo} - CVSS v2 Exploitability Score before SECURITY.md commits', dates, v2_e, v2_legends, colors, f'cvss/v2/exploitability/{file_name}.png')
    chart.plot2(f'{repo} - CVSS v3 Impact Score before SECURITY.md commits', dates, v3_i, v3_legends, colors, f'cvss/v3/impact/{file_name}.png')
    chart.plot2(f'{repo} - CVSS v3 Exploitability Score Score before SECURITY.md commits', dates, v3_e, v3_legends, colors, f'cvss/v3/exploitability/{file_name}.png')


def get_dates(repo):
    dates = []
    yesterday_dates = []
    file_path = '_'.join(repo.split('/'))
    file_path = f'./content/{file_path}.csv'
    writer = csv_writer(file_path)
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance', 'bcompare'])
    for i in range(1, len(rows)):
        date_time = datetime.strptime(rows[i][3], '%Y-%m-%d %H:%M:%S%z')
        date = int(f'{date_time}'[:10].replace('-', ''))
        yesterday_date = int(f'{date_time - timedelta(days=1)}'[:10].replace('-', ''))
        if date not in dates and yesterday_date not in yesterday_dates:
            dates.append(date)
            yesterday_dates.append(yesterday_date)
    return dates, yesterday_dates


if __name__ == '__main__':
    for repo in repository.get_list(2):
        print(repo)
        dates, yesterday_dates = get_dates(repo)
        if len(dates) > 0:
            generate_charts(repo, dates, yesterday_dates)
        else:
            print('no commit history')
