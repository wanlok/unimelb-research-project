from math import floor, ceil

import numpy as np
from matplotlib import pyplot as plt

font_name = 'Times New Roman'
font = {'fontname': font_name}
padding_1 = 16
padding_2 = 24

def plot(title, x, y, file_path):
    fig = plt.figure()
    fig.set_size_inches(len(x) * 2, 8)
    plt.bar(x, y, color='black', width=0.24)
    plt.xticks(rotation=45, fontname=font_name)
    plt.xlabel('SECURITY.md Update Dates', fontdict=font, labelpad=padding_2)
    plt.yticks(range(floor(min(y)), ceil(max(y)) + 1, 50), fontname=font_name)
    plt.ylabel('Number of CVEs Before Updates', fontdict=font, labelpad=padding_2)
    plt.title(title, fontdict=font, pad=padding_2)
    ax = plt.gca()
    for i in range(len(y)):
        rect = ax.patches[i]
        ax.text(rect.get_x() + rect.get_width() / 2, y[i], f'{y[i]}\n', ha='center', fontdict=font)
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
    ax.tick_params(axis='x', pad=padding_1)
    ax.tick_params(axis='y', pad=padding_1)
    plt.title(title, fontdict=font, pad=padding_1)
    plt.setp(ax.legend(loc='upper left').texts, family=font_name)
    ax.set_ylim([0, length])
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()