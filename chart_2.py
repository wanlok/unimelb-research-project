import sys
from datetime import datetime, timedelta

import commit_history
import repository
from chart import plot


markdown_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'
chart_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\2\\'


def dummy_by_month(repo):
    my_dict = commit_history.get_content_by_month('./data/securities/', repo)
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
    my_dict = commit_history.get_content_by_day('./data/securities/', repo)
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
    x_title = 'SECURITY.md Update Dates (Number of Updates)'
    y_title = 'Number of Commits'
    for repo in repository.get_list(334, 9999):
        print(repo)
        x_values, y_values = dummy_by_day(repo)
        if len(x_values) == len(y_values) and len(x_values) > 0:
            slices = repo.split('/')
            file_name = '_'.join(slices)
            # append_html(writer, number_of_rows, date_dict, file_name)
            plot(repo, x_values, y_values, x_title, y_title, f'{chart_path}{file_name}.png')
