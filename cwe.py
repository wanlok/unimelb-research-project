import sys

import nvdcve
from utils import csv_reader

cwe_csv_file_path = 'C:\\Files\\Projects\\1000.csv'


def get_cwe_dict(cve_list, year_month=None):
    cwe_dict = dict()
    for i in range(len(cve_list)):
        cve_id, date, _, _, _, _, cwe_ids, _ = cve_list[i]
        if year_month is not None and year_month not in date:
            continue
        cwe_ids = eval(cwe_ids)
        for cwe_id in cwe_ids:
            if cwe_id in cwe_dict:
                if date in cwe_dict[cwe_id]:
                    cwe_dict[cwe_id][date].append(cve_id)
                else:
                    cwe_dict[cwe_id][date] = [cve_id]
            else:
                cwe_dict[cwe_id] = dict()
                cwe_dict[cwe_id][date] = [cve_id]
    return cwe_dict


def get_cwe_sorted_list(cwe_dict):
    cwe_list = []
    for cwe_id in cwe_dict:
        date_dict = cwe_dict[cwe_id]
        length = len(cwe_list)
        index = length
        for i in range(length):
            sum_1 = sum(list(map(lambda x: len(x), date_dict.values())))
            sum_2 = sum(list(map(lambda x: len(x), cwe_list[i][1].values())))
            if sum_1 < sum_2:
                index = i
                break
        cwe_list.insert(index, [cwe_id, date_dict])
    return cwe_list


def get_cwe_names(cwe_ids):
    targets = []
    for row in csv_reader(cwe_csv_file_path):
        for cwe_id in cwe_ids:
            if cwe_id[4:] == row[0]:
                targets.append([cwe_id, row[1]])
    return targets


def get_cwe_name(cwe_names, cwe_id):
    cwe_name = None
    for i in range(len(cwe_names)):
        if cwe_id == cwe_names[i][0]:
            cwe_name = cwe_names[i][1]
            break
    return cwe_name


if __name__ == '__main__':
    cve_list = nvdcve.get_list(sys.argv[1])
    if len(sys.argv) > 2:
        cwe_dict = get_cwe_dict(cve_list, sys.argv[2])
    else:
        cwe_dict = get_cwe_dict(cve_list)
    cwe_names = get_cwe_names(cwe_dict)
    for cwe in get_cwe_sorted_list(cwe_dict):
        cwe_id, dates = cwe
        cwe_sum = 0
        cwe_max = None
        for date in cwe_dict[cwe_id]:
            length = len(cwe_dict[cwe_id][date])
            cwe_sum = cwe_sum + length
            if cwe_max is None or length > cwe_max:
                cwe_max = length
        print(f'{cwe_id} {get_cwe_name(cwe_names, cwe_id)}')
        print(f'SUM: {cwe_sum}, MAX: {cwe_max}')
        for date in dates:
            print(f'{date} {len(dates[date])} {dates[date]}')
        print(f'')
