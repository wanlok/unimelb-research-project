import os
from datetime import datetime, timedelta

import commit_history
import repository
from chart import plot, scatter_plot
from security_md import get_date_statistics
from utils import get_start_and_end_date_string_before_date_minus_days

markdown_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'
chart_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\2\\'


def dummy_by_month(repo):
    my_dict = commit_history.get_content_by_month('data/securities/', repo)
    keys = list(my_dict.keys())
    keys.sort()
    for key in keys:
        year = int(f'{key}'[:4])
        month = int(f'{key}'[4:])
        start_month = '{:02d}'.format(month)
        start_date = datetime.strptime(f'{year}{start_month}01', '%Y%m%d').strftime('%Y%m%d')
        if month == 12:
            year = year + 1
            month = 1
        else:
            month = month + 1
        end_month = '{:02d}'.format(month)
        end_date = (datetime.strptime(f'{year}{end_month}01', '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')
        commit_count = repository.get_commit_count(repo, start_date, end_date)
        print(f'{start_date} {end_date} {len(my_dict[key])} {commit_count}')


def dummy_by_day(repo):
    my_dict = commit_history.get_content_by_day('data/securities/', repo)
    keys = list(my_dict.keys())
    keys.sort()
    x = []
    y = []
    for key in keys:
        print(f'checking {repo} {key}')
        x.append(f'{key} ({len(my_dict[key])})')
        y.append(repository.get_commit_count(repo, f'{key}', f'{key}'))
    return x, y


if __name__ == '__main__':
    number_of_days_before = 100
    x_title = "SECURITY.md Update Dates (Number of Updates)"
    y_title = f"Number of Commits {number_of_days_before} Days Before"
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
            for date in date_list:
                start_date, end_date = get_start_and_end_date_string_before_date_minus_days(datetime.strptime(date, '%Y%m%d'), number_of_days_before, '%Y%m%d')
                number_of_security_md_commits = date_dict[date]
                x_values.append(f'{date} ({number_of_security_md_commits})')
                x_all_values.append(number_of_security_md_commits)
                y_values.append(repository.get_commit_count(repo, start_date, end_date))
            y_all_values.extend(y_values)
            plot(repo, x_values, y_values, x_title, y_title, f'{chart_path}{file_name}.png')
    scatter_plot(x_all_values, y_all_values, f'{chart_path}distribution.png')
