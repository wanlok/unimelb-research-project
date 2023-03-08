import sys

from Levenshtein import distance

from utils import csv_reader, csv_writer, prepare_csv_file

if __name__ == '__main__':
    if len(sys.argv) > 1:
        content_csv_file_path = 'content.csv'
        content_csv_reader = csv_reader(content_csv_file_path)
        compare_csv_file_path = 'compare.csv'
        compare_csv_writer = csv_writer(compare_csv_file_path, mode='w')
        compare_csv_reader = csv_reader(compare_csv_file_path)
        compare_csv_rows = prepare_csv_file(compare_csv_reader, compare_csv_writer, ['dominant_content', 'content', 'levenshtein_distance', 'occurrence'])
        content_dict = {}
        i = 0
        for row in content_csv_reader:
            if i > 0:
                if sys.argv[1].lower() in row[2].lower():
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
                compare_csv_writer.writerow([dominant_content, content, distance(dominant_content, content), content_dict[key]])
