from datetime import datetime
from math import floor, ceil
from os.path import exists
from statistics import mean, stdev

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator, MultipleLocator
from scipy.stats import pearsonr

import repository
from repository import get_list
from security_md import get_date_statistics, get_date_statistics_with_zeros

font_name = 'Times New Roman'
font = {'fontname': font_name}
padding_1 = 8
padding_2 = 16
padding_3 = 24

security_md_directory_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\data\\securities\\'


def security_dummy(start_date, end_date, y_function):
    x_title = f'Number of SECURITY.md Commits'
    x_all_values = []
    y_all_values = []
    i = 0

    repos = get_list()
    print(len(repos))

    for repo in get_list(10):
        file_name = '_'.join(repo.split('/'))
        file_path = f'{security_md_directory_path}{file_name}.csv'
        if exists(file_path):
            _, date_dict = get_date_statistics(file_path, start_date, end_date)
            # commit_dict = get_monthly_commit_statistics(repo, start_date, end_date)
            number_of_security_md_commits = sum(date_dict.values())
            # number_of_commits = sum(commit_dict.values())
            # if number_of_security_md_commits > 0 and number_of_commits > 0:
            #     print(f'{repo} Number of SECURITY.md Commits: {number_of_security_md_commits}, Number of Commits: {number_of_commits}')
            x_all_values.append(number_of_security_md_commits)

    # x_all_values = numpy.array(x_all_values)
    # print(x_all_values)
    mean_val = mean(x_all_values)
    print(x_all_values)
    print(mean_val)
    sd_val = stdev(x_all_values)

    plt.hist(x_all_values, bins=max(x_all_values), density=True)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Normal Distribution Curve')

    plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2)
    plt.axvline(mean_val - sd_val, color='green', linestyle='dashed', linewidth=2)
    plt.axvline(mean_val + sd_val, color='green', linestyle='dashed', linewidth=2)

    plt.show()


def security_md_plot(start_date, end_date, y_function, title, y_title, save_file_path):
    x_title = f'Number of SECURITY.md Commits'
    x_values = []
    y_values = []
    for repo in get_list():
        file_name = '_'.join(repo.split('/'))
        file_path = f'{security_md_directory_path}{file_name}.csv'
        if exists(file_path):
            x_value = sum(get_date_statistics(file_path, start_date, end_date)[1].values())
            y_value = y_function(repo, start_date, end_date)
            print(f'{repo} {x_value} {y_value}')
            x_values.append(x_value)
            y_values.append(y_value)
    scatter_plot(x_values, y_values, title, x_title, y_title, save_file_path)
    correlation_coefficient, p_value = pearsonr(x_values, y_values)
    print(f'{correlation_coefficient} {p_value}')


def security_md_by_date_plot(date_function, y_function, y_title, chart_directory_path):
    number_of_days_before = 100
    x_title = f'SECURITY.md Update Dates (Number of Updates)'
    y_title = y_title.replace('{}', f'{number_of_days_before}')
    x_all_values = []
    y_all_values = []
    for repo in get_list(2):
        file_name = '_'.join(repo.split('/'))
        file_path = f'{security_md_directory_path}{file_name}.csv'
        if exists(file_path):
            print(repo)
            x_values = []
            y_values = []
            date_list, date_dict = get_date_statistics(file_path)
            # for date in date_list:
            #     print(date)

            if len(date_list) > 0:
                start = datetime.strptime(f'{min(date_list)}', '%Y%m%d').strftime('%m/%d/%Y')
                end = datetime.strptime(f'{max(date_list)}', '%Y%m%d').strftime('%m/%d/%Y')
                date_range = pd.date_range(start=start, end=end, freq='D')
                i = 0
                for date in date_range:
                    i = i + 1
                    print(f'{i} {date}')
                # data = {'datatime': pd.date_range(start=start, end=end, freq='D'),
                #         'dummy': []}



                # start_date, end_date = date_function(datetime.strptime(f'{date}', '%Y%m%d'), number_of_days_before, '%Y%m%d')

                # number_of_security_md_commits = date_dict[date]
                # print(number_of_security_md_commits)
                # x_values.append(f'{date} ({number_of_security_md_commits})')
                # x_all_values.append(number_of_security_md_commits)
                # y_values.append(y_function(repo, start_date, end_date))
    #         y_all_values.extend(y_values)
    #         plot(repo, x_values, y_values, x_title, y_title, f'{chart_directory_path}{file_name}.png')
    # scatter_plot(x_all_values, y_all_values, '', '', '', f'{chart_directory_path}distribution.png')


def scatter_plot(x_values, y_values, title, x_title, y_title, file_path):
    # print(f'validate: {len(x_values) * 2}')
    if len(x_values) == len(y_values) and len(x_values) > 0:
        fig = plt.figure()
        h = 8
        fig.set_size_inches(max(x_values) * 0.5, h)
        ax = fig.gca()
        ax.tick_params(axis='x', pad=padding_1)
        ax.tick_params(axis='y', pad=padding_1)
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        # ax.margins(x=0.1, y=0.1)
        plt.scatter(x_values, y_values, color='black')
        if max(y_values) <= h:
            dummy = 1
        else:
            dummy = int(max(y_values) / h)
        plt.yticks(range(floor(min(y_values)), ceil(max(y_values)), dummy), fontname=font_name)
        plt.ylabel(y_title, fontdict=font, labelpad=padding_2)
        plt.title(title, fontdict=font, pad=padding_3)
        plt.xlim(0, max(x_values))
        plt.ylim(0, max(y_values))
        plt.xticks(fontname=font_name)
        plt.xlabel(x_title, fontdict=font, labelpad=padding_2)
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()


def line_chart(x_values, y_values, x_ticks, title, x_title, y_title):
    plt.plot(x_values, y_values)
    plt.title(title)
    plt.xticks(x_ticks)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()


def plot(title, x_values, y_values, x_title, y_title, file_path):
    if len(x_values) == len(y_values) and len(x_values) > 0:
        fig = plt.figure()
        h = 8
        fig.set_size_inches(len(x_values) * 2, h)
        ax = plt.gca()
        ax.tick_params(axis='x', pad=padding_2)
        ax.tick_params(axis='y', pad=padding_2)
        plt.bar(x_values, y_values, color='black', width=0.24)
        # plt.xticks(fontname=font_name, rotation=45)
        plt.xticks(fontname=font_name)
        plt.xlabel(x_title, fontdict=font, labelpad=padding_3)
        if max(y_values) <= h:
            dummy = 1
        else:
            dummy = int(max(y_values) / h)
        plt.yticks(range(floor(min(y_values)), ceil(max(y_values)) + 1, dummy), fontname=font_name)
        plt.ylabel(y_title, fontdict=font, labelpad=padding_3)
        plt.title(title, fontdict=font, pad=padding_3)
        ax = plt.gca()
        for i in range(len(y_values)):
            rect = ax.patches[i]
            ax.text(rect.get_x() + rect.get_width() / 2, y_values[i], f'{y_values[i]}\n', ha='center', fontdict=font)
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()


def plot2(title, x, y, legends, colors, file_path):
    weight_counts = dict()
    length = 0
    for i in range(len(y)):
        length = sum(y[i])
        for j in range(len(legends)):
            if j in weight_counts:
                weight_counts[j].append(y[i][j])
            else:
                weight_counts[j] = [y[i][j]]
    fig = plt.figure()
    fig.set_size_inches(len(x) * 1, 8)
    length = length + (length * 0.04)
    width = 0.56
    species = list(map(lambda x: f'{x}', x))
    ax = plt.gca()
    bottom = np.zeros(len(species))
    for i, weight_count in weight_counts.items():
        ax.bar(species, weight_count, width, bottom=bottom, label=legends[i], color=colors[i])
        bottom += weight_count
    for container in ax.containers:
        labels = [int(value) if value > 0 else '' for value in container.datavalues]
        ax.bar_label(container, labels=labels, label_type='center', **font)
    plt.xticks(font=font_name)
    plt.yticks(font=font_name)
    ax.tick_params(axis='x', pad=padding_2)
    ax.tick_params(axis='y', pad=padding_2)
    plt.title(title, fontdict=font, pad=padding_2)
    plt.setp(ax.legend(loc='upper left').texts, family=font_name)
    ax.set_ylim([0, length])
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()


def dummy(repos, start_date, end_date, title, file_path):
    x_values = None
    aggregated_y_values = None
    fig = plt.figure()
    for repo in repos:
        print(repo)
        repo_file_name = '_'.join(repo.split('/'))
        repo_file_path = f'{security_md_directory_path}{repo_file_name}.csv'
        date_list, date_dict = get_date_statistics_with_zeros(repo_file_path, start_date, end_date)
        if x_values is None:
            x_values = []
            for date in date_list:
                x_value = f'{date}'
                if x_value[6:] == '01':
                    x_values.append(x_value[:6])
                else:
                    x_values.append(x_value)
            fig.set_size_inches(len(x_values) * 0.08, 6)
        y_values = []
        for date in date_list:
            if date_dict[date] > 0:
                y_values.append(1)
            else:
                y_values.append(0)
        if sum(y_values) > 0:
            if aggregated_y_values is None:
                aggregated_y_values = np.zeros(len(y_values))
                plt.bar(x_values, y_values, align='edge')
            else:
                plt.bar(x_values, y_values, bottom=aggregated_y_values, align='edge')
            aggregated_y_values = aggregated_y_values + y_values
    print(aggregated_y_values)
    if x_values is not None:
        max_aggregated_y_value = int(max(aggregated_y_values))
        ax = fig.gca()
        ax.tick_params(axis='x', pad=padding_1)
        ax.tick_params(axis='y', pad=padding_1)
        x_ticks = list(filter(lambda x: len(x) == 6, x_values))
        plt.xticks(x_ticks, font=font_name)
        plt.yticks(range(0, max_aggregated_y_value + 1), font=font_name)
        # plt.xlim(x_values[0], x_values[-1])
        plt.ylim(0, max_aggregated_y_value + 0.2)
        plt.title(title, fontdict=font, pad=padding_2)
        plt.xlabel('Dates', fontdict=font, labelpad=padding_2)
        plt.ylabel('Number of Repositories', fontdict=font, labelpad=padding_2)
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()

