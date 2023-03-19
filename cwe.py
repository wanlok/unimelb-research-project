import sys

from utils import csv_reader


def get_cve_list(repo, on_or_after_date):
    targets = []
    directory_path = f'C:\\Files\\Projects\\'
    file_path = f'{directory_path}nvdcve.csv'
    i = 0
    for row in csv_reader(file_path):
        if i > 0:
            if int(row[1]) >= int(on_or_after_date) and repo.lower() in row[3].lower():
                targets.append(row)
        i = i + 1
    return targets


def get_cve_dict(cves):
    cwe_dict = dict()
    for i in range(len(cves)):
        cve_id, date, cwe_ids, _ = cves[i]
        cwe_ids = eval(cwe_ids)
        # print(f'{i + 1} {cve_id} {date} {cwe_ids}')
        for cwe_id in cwe_ids:
            if cwe_id in cwe_dict:
                if date in cwe_dict[cwe_id]:
                    cwe_dict[cwe_id][date] = cwe_dict[cwe_id][date] + 1
                else:
                    cwe_dict[cwe_id][date] = 1
            else:
                cwe_dict[cwe_id] = dict()
                cwe_dict[cwe_id][date] = 1
    return cwe_dict


def get_cwe_names(cwe_ids):
    targets = []
    cwe_csv_file_path = 'C:\\Files\\Projects\\1000.csv'
    for row in csv_reader(cwe_csv_file_path):
        for cwe_id in cwe_ids:
            if cwe_id[4:] == row[0]:
                targets.append([cwe_id, row[1]])
    return targets


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cve_list = get_cve_list(sys.argv[1], sys.argv[2])
    else:
        cve_list = get_cve_list(sys.argv[1], 0)
    cwe_list = []
    cwe_dict = get_cve_dict(cve_list)
    for cwe_id in cwe_dict:
        date_dict = cwe_dict[cwe_id]
        length = len(cwe_list)
        index = length
        for i in range(length):
            if sum(date_dict.values()) < sum(cwe_list[i][1].values()):
                index = i
                break
        cwe_list.insert(index, [cwe_id, date_dict])
    cwe_names = get_cwe_names(cwe_dict)
    for cwe in cwe_list:
        cwe_id = cwe[0]
        cwe_name = None
        for i in range(len(cwe_names)):
            if cwe_id == cwe_names[i][0]:
                cwe_name = cwe_names[i][1]
                break
        cwe_sum = sum(cwe_dict[cwe_id].values())
        cwe_max = max(cwe_dict[cwe_id].values())
        cwe_max_dates = []
        for date in cwe_dict[cwe_id]:
            if cwe_dict[cwe_id][date] == cwe_max:
                cwe_max_dates.append(date)
        print(f'{cwe_id} {cwe_name}')
        print(f'SUM: {cwe_sum}, MAX: {cwe_max} {cwe_max_dates}')
        print(f'{cwe_dict[cwe_id]}')
        print(f'')