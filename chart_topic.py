from datetime import datetime

import repository
from chart import plot
from security_md import get_date_statistics

security_md_directory_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'

if __name__ == '__main__':
    keyword = 'java'
    # with_security_md_repos, without_security_md_repos = repository.search_by_categories(['react'], ['azureactivedirectory', 'reactive', 'reactive-programming'])
    # with_security_md_repos, without_security_md_repos = repository.search_by_categories(['vue'])
    # with_security_md_repos, without_security_md_repos = repository.search_by_categories(['angular'])
    # with_security_md_repos, without_security_md_repos = repository.search_by_categories(['javascript'])
    with_security_md_repos, without_security_md_repos = repository.search_by_categories(['java'], ['javascript', 'javascipt', 'js'])
    # with_security_md_repos, without_security_md_repos = repository.search_by_categories([keyword])
    year_month_dict = dict()
    title = keyword
    x_title = 'Year Month'
    y_title = 'Number of SECURITY.md changes'
    x_values = []
    y_values = []
    for repo in with_security_md_repos:
        file_name = '_'.join(repo.split('/'))
        file_path = f'{security_md_directory_path}{file_name}.csv'
        date_dict = get_date_statistics(file_path, 20210000, 20219999)[1]
        for date in date_dict:
            year_month = int(datetime.strptime(f'{date}', '%Y%m%d').strftime('%Y%m'))
            if year_month in year_month_dict:
                if date in year_month_dict[year_month]:
                    year_month_dict[year_month][date].append((repo, date_dict[date]))
                else:
                    year_month_dict[year_month][date] = [(repo, date_dict[date])]
            else:
                length = len(x_values)
                index = length
                for i in range(length):
                    if year_month < x_values[i]:
                        index = i
                        break
                x_values.insert(index, year_month)
                year_month_date_dict = dict()
                year_month_date_dict[date] = [(repo, date_dict[date])]
                year_month_dict[year_month] = year_month_date_dict
    for year_month in x_values:
        print(f'{year_month} {year_month_dict[year_month]}')
        y_value = 0
        for date in year_month_dict[year_month]:
            for repo in year_month_dict[year_month][date]:
                y_value = y_value + repo[1]
        y_values.append(y_value)
    x_values = list(map(lambda x: f'{x}', x_values))
    print(x_values)
    print(y_values)
    print(sum(y_values))
    file_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\{keyword}.png'
    plot(title, x_values, y_values, x_title, y_title, file_path)
