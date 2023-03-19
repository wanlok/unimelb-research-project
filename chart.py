from math import floor, ceil

from matplotlib import pyplot as plt


def plot(title, x, y, file_path):
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
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()