from utils import csv_reader

if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_reader = csv_reader(content_csv_file_path)
    i = 0
    dict = {}
    for row in content_csv_reader:
        if i > 0:
            if 'Use this section to tell people about which' in row[2]:
                if row[2] in dict:
                    dict[row[2]] = dict[row[2]] + 1
                else:
                    dict[row[2]] = 1
        i = i + 1
    print('# Security Policy\n\n## Supported Versions\n\nUse this section to tell people about which versions of your project are\ncurrently being supported with security updates.\n\n| Version | Supported          |\n| ------- | ------------------ |\n| 5.1.x   | :white_check_mark: |\n| 5.0.x   | :x:                |\n| 4.0.x   | :white_check_mark: |\n| < 4.0   | :x:                |\n\n## Reporting a Vulnerability\n\nUse this section to tell people how to report a vulnerability.\n\nTell them where to go, how often they can expect to get an update on a\nreported vulnerability, what to expect if the vulnerability is accepted or\ndeclined, etc.\n')
    print(f'total {len(dict)}')
    largest = 1
    for key in dict:
        if dict[key] > largest:
            


