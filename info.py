from utils import csv_reader, csv_writer, prepare_csv_file

if __name__ == '__main__':
    # content_csv_file_path = 'content.csv'
    # content_csv_reader = csv_reader(content_csv_file_path)
    info_file_path = 'info.csv'
    info_writer = csv_writer(info_file_path, mode='w')
    info_reader = csv_reader(info_file_path)
    info_rows = prepare_csv_file(info_reader, info_writer, ['repo', 'file_from_parent'])
    # i = 0
    # for row in content_csv_reader:
    #     if i > 0:
    #         content = eval(row[2]).decode('utf-8')
    #         headings = re.findall(r'[b\'|b\"|\\n]#+ *(.*?) *\\n', row[2])
    #         cve_count = content.lower().count('cve')
    #         language = langid.classify(content)[0].upper()
    #         content_info_csv_writer.writerow([row[0], row[1], len(headings), language, cve_count])
    #     i = i + 1
