import sys

from utils import csv_reader, csv_writer

if __name__ == '__main__':
    if len(sys.argv) > 1:
        content_csv_file_path = 'content.csv'
        content_csv_reader = csv_reader(content_csv_file_path)
        compare_csv_file_path = 'compare.csv'
        compare_csv_writer = csv_writer(compare_csv_file_path, mode='w')
        content_dict = {}
        i = 0
        for row in content_csv_reader:
            if i > 0:
                if sys.argv[1] in row[2]:
                    if row[2] in content_dict:
                        content_dict[row[2]] = content_dict[row[2]] + 1
                    else:
                        content_dict[row[2]] = 1
            i = i + 1
        largest = None
        dominant_content = None
        if len(content_dict) > 0:
            for key in content_dict:
                if largest is None or content_dict[key] > largest:
                    largest = content_dict[key]
                    dominant_content = key
            dominant_content = dominant_content.replace('\\n', '\n')
        for key in content_dict:
            content = key.replace('\\n', '\n')
            if content != dominant_content:
                compare_csv_writer.writerow([dominant_content, content, content_dict[key]])
