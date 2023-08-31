from xml.dom import minidom

from document.rq2 import get_column_title_and_values
from utils import sort_by_ascending_keys


def get_owasp_cwe_mappings():
    mappings = []
    directory_path = f'C:\\Files\\OWASP Top Ten\\'
    years = [2017, 2021]
    for year in years:
        file_name = f'{year}.xml'
        file = minidom.parse(f'{directory_path}{file_name}')
        i = 0
        for category in file.getElementsByTagName('Category'):
            name = category.attributes['Name'].value
            if f'{year}' in name:
                i = i + 1
                name = name.replace(f'OWASP Top Ten {year} Category ', '').replace(f':{year}', '').replace(' - ', ' ')
                slices = name.split(' ')
                name = ' '.join(slices[1:])
                cwe_ids = []
                for relationship in category.getElementsByTagName('Relationships'):
                    for has_member in relationship.getElementsByTagName('Has_Member'):
                        cwe_id = has_member.attributes['CWE_ID'].value
                        cwe_ids.append(f'CWE-{cwe_id}')
                mappings.append((year, f'A{i}', name, cwe_ids))
    return mappings


def aaa(name):
    name = name.replace('Cross Site', 'Cross-Site')
    name = name.replace(' Flaws', '')
    name = name.replace('Forgery(CSRF)', 'Forgery (CSRF)')
    if name == 'Insecure Direct Object Reference':
        name = 'Insecure Direct Object References'
    if name == 'Broken Authentication':
        name = 'Broken Authentication and Session Management'
    return name


if __name__ == '__main__':
    name_dict = dict()
    mappings = get_owasp_cwe_mappings()
    for mapping in mappings:
        year = mapping[0]
        name = aaa(mapping[2])
        cwes = mapping[3]
        if name in name_dict:
            name_dict[name].append((year, cwes))
        else:
            name_dict[name] = [(year, cwes)]
    for name in sort_by_ascending_keys(name_dict):
        # years = ','.join(name_dict[name])
        year_set = set()
        cwe_set = set()
        for year, cwes in name_dict[name]:
            year_set.add(year)
            cwe_set.update(cwes)
        print(f'"{name}","{year_set}","{cwe_set}"')


    # title, values = get_column_title_and_values(34, True)
    #
    # for value in values:
    #     print(value)
