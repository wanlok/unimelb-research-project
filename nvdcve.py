

def list_dummy():
    targets = []
    directory_path = 'C:\\Files\\Projects\\nvdcve\\'
    for file_name in os.listdir(directory_path):
        slices = file_name.split('.')
        if slices[len(slices) - 1] == 'json':
            file_path = f'{directory_path}{file_name}'
            print(file_path)
            f = open(file_path, encoding='latin-1')
            data = json.load(f)
            for item in data['CVE_Items']:
                # if repo in ''.join():
                cve_id = item['cve']['CVE_data_meta']['ID']
                date = datetime.strptime(item['publishedDate'], '%Y-%m-%dT%H:%MZ')
                date = int(f'{date.year}{"{:02d}".format(date.month)}{"{:02d}".format(date.day)}')
                cwe_ids = list(filter(lambda x: x != 'NVD-CWE-noinfo' and x != 'NVD-CWE-Other', list(itertools.chain(*list(map(lambda x: list(map(lambda x: x['value'], x['description'])), item['cve']['problemtype']['problemtype_data']))))))
                urls = list(map(lambda x: x['url'], item['cve']['references']['reference_data']))
                length = len(targets)
                index = length
                for j in range(length):
                    if date < targets[j][1]:
                        index = j
                        break
                targets.insert(index, [cve_id, date, cwe_ids, urls])
    file_path = f'{directory_path}combine.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['cve_id', 'date', 'cwe_ids', 'urls'])
    for target in targets:
        writer.writerow(target)
    return targets