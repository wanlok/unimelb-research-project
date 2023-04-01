import itertools
import json
import os
from datetime import datetime

from utils import csv_writer, csv_reader, prepare_csv_file

directory_path = 'C:\\Files\\Projects\\nvdcve\\'


def get_list(repo, start_date=0, end_date='99999999'):
    targets = []
    directory_path = f'C:\\Files\\Projects\\'
    file_path = f'{directory_path}nvdcve.csv'
    start_date = int(start_date)
    end_date = int(end_date)
    i = 0
    for row in csv_reader(file_path):
        if i > 0:
            if repo.lower() in row[7].lower() and start_date <= int(row[1]) <= end_date:
                targets.append(row)
        i = i + 1
    return targets


def is_exists(repo, up_to_date='99999999'):
    exists = False
    directory_path = f'C:\\Files\\Projects\\'
    file_path = f'{directory_path}nvdcve.csv'
    up_to_date = int(up_to_date)
    i = 0
    for row in csv_reader(file_path):
        if i > 0:
            if int(row[1]) <= up_to_date and repo.lower() in row[7].lower():
                exists = True
                break
        i = i + 1
    return exists


if __name__ == '__main__':
    targets = []
    for file_name in os.listdir(directory_path):
        slices = file_name.split('.')
        if slices[len(slices) - 1] == 'json':
            file_path = f'{directory_path}{file_name}'
            print(file_path)
            f = open(file_path, encoding='latin-1')
            data = json.load(f)
            for item in data['CVE_Items']:
                cve_id = item['cve']['CVE_data_meta']['ID']
                date = datetime.strptime(item['publishedDate'], '%Y-%m-%dT%H:%MZ')
                date = int(f'{date.year}{"{:02d}".format(date.month)}{"{:02d}".format(date.day)}')
                impact = item['impact']
                if 'baseMetricV2' in impact:
                    cvss_v2_impact_score = impact['baseMetricV2']['impactScore']
                    cvss_v2_exploitability_score = impact['baseMetricV2']['exploitabilityScore']
                else:
                    cvss_v2_impact_score = ''
                    cvss_v2_exploitability_score = ''
                if 'baseMetricV3' in impact:
                    cvss_v3_impact_score = impact['baseMetricV3']['impactScore']
                    cvss_v3_exploitability_score = impact['baseMetricV3']['exploitabilityScore']
                else:
                    cvss_v3_impact_score = ''
                    cvss_v3_exploitability_score = ''
                cwe_ids = list(filter(lambda x: x != 'NVD-CWE-noinfo' and x != 'NVD-CWE-Other', list(itertools.chain(*list(map(lambda x: list(map(lambda x: x['value'], x['description'])), item['cve']['problemtype']['problemtype_data']))))))
                urls = list(map(lambda x: x['url'], item['cve']['references']['reference_data']))
                length = len(targets)
                index = length
                for j in range(length):
                    if date < targets[j][1]:
                        index = j
                        break
                row = [cve_id, date, cvss_v2_impact_score, cvss_v2_exploitability_score, cvss_v3_impact_score, cvss_v3_exploitability_score, cwe_ids, urls]
                targets.insert(index, row)
            # break
    file_path = f'{directory_path}combine.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    prepare_csv_file(reader, writer, ['cve_id', 'date', 'cvss_v2_impact_score', 'cvss_v2_exploitability_score', 'cvss_v3_impact_score', 'cvss_v3_exploitability_score', 'cwe_ids', 'urls'])
    for target in targets:
        writer.writerow(target)
