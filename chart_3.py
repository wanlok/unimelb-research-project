import os
from datetime import datetime

import repository
from chart import plot, scatter_plot
from utils import csv_reader, get_start_and_end_date_string

markdown_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'
chart_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\3\\'


if __name__ == '__main__':
    x_title = "SECURITY.md Update Years and Months (Number of Updates)"
    y_title = "Number of Issues"
    x_all_values = []
    y_all_values = []
    for repo in repository.get_list():
        slices = repo.split('/')
        file_name = '_'.join(slices)
        file_path = f'{markdown_path}{file_name}.csv'
        if os.path.exists(file_path):
            dummy_dict = dict()
            for row in csv_reader(file_path):
                try:
                    key = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m')
                    if key in dummy_dict:
                        dummy_dict[key].append(row)
                    else:
                        dummy_dict[key] = [row]
                except ValueError:
                    pass
            print(repo)
            x_values = []
            y_values = []
            fixed_start = None
            for year_month in dummy_dict:
                start_date, end_date = get_start_and_end_date_string(f'{year_month}01')
                if fixed_start is None:
                    fixed_start = start_date
                x_values.append(f'{year_month} ({len(dummy_dict[year_month])})')
                x_all_values.append(len(dummy_dict[year_month]))
                y_values.append(repository.get_issue_count(repo, fixed_start, end_date))
            y_all_values.extend(y_values)
            plot(repo, x_values, y_values, x_title, y_title, f'{chart_path}{file_name}.png')
    scatter_plot(x_all_values, y_all_values, f'{chart_path}distribution.png')
