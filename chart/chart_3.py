from chart import security_md_by_date_plot
from repository import get_issue_count
from utils import get_start_and_end_date_string_before_date_minus_days

date_function = get_start_and_end_date_string_before_date_minus_days
y_function = get_issue_count
y_title = 'Number of Issues {} Days Before'
chart_directory_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\3\\'


if __name__ == '__main__':
    security_md_by_date_plot(date_function, y_function, y_title, chart_directory_path)


# if __name__ == '__main__':
#     number_of_days_before = 100
#     x_title = "SECURITY.md Update Dates (Number of Updates)"
#     y_title = f"Number of Issues {number_of_days_before} Days Before"
#     x_all_values = []
#     y_all_values = []
#     for repo in repository.get_list(200):
#         slices = repo.split('/')
#         file_name = '_'.join(slices)
#         file_path = f'{markdown_path}{file_name}.csv'
#         if os.path.exists(file_path):
#             # dummy_dict = dict()
#             # for row in csv_reader(file_path):
#             #     try:
#             #         key = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m')
#             #         if key in dummy_dict:
#             #             dummy_dict[key].append(row)
#             #         else:
#             #             dummy_dict[key] = [row]
#             #     except ValueError:
#             #         pass
#
#             print(repo)
#             x_values = []
#             y_values = []
#             date_list, date_dict = get_date_statistics(file_path)
#             for date in date_list:
#                 start_date, end_date = get_start_and_end_date_string_before_date_minus_days(datetime.strptime(date, '%Y%m%d'), number_of_days_before, '%Y%m%d')
#                 number_of_security_md_commits = date_dict[date]
#                 x_values.append(f'{date} ({number_of_security_md_commits})')
#                 x_all_values.append(number_of_security_md_commits)
#                 y_values.append(repository.get_issue_count(repo, start_date, end_date))
#
#             # fixed_start = None
#             # for year_month in dummy_dict:
#             #     start_date, end_date = get_start_and_end_date_string(f'{year_month}01')
#             #     if fixed_start is None:
#             #         fixed_start = start_date
#             #     x_values.append(f'{year_month} ({len(dummy_dict[year_month])})')
#             #     x_all_values.append(len(dummy_dict[year_month]))
#             #     y_values.append(repository.get_issue_count(repo, fixed_start, end_date))
#             y_all_values.extend(y_values)
#             plot(repo, x_values, y_values, x_title, y_title, f'{chart_path}{file_name}.png')
#     scatter_plot(x_all_values, y_all_values, f'{chart_path}distribution.png')
