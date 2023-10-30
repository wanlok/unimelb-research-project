import re
from xml.dom import minidom

from utils import get_latest_content, get_file_path, get_column_title_and_values, get_grouped_column_title_and_values, \
    repos


def get_owasp_cwe_mappings(years):
    mappings = []
    directory_path = f'C:\\Files\\Projects\\OWASP Top Ten\\'
    # years = [2017, 2021]
    # years = [2004, 2007, 2010, 2013, 2017, 2021]
    for year in years:
        file_name = f'{year}.xml'
        file = minidom.parse(f'{directory_path}{file_name}')
        i = 0
        for category in file.getElementsByTagName('Category'):
            description = category.attributes['Name'].value
            if f'{year}' in description:
                i = i + 1
                description = description.replace(f'OWASP Top Ten {year} Category ', '').replace(f':{year}', '').replace(' - ', ' ')
                slices = description.split(' ')
                description = ' '.join(slices[1:])
                cwe_ids = []
                for relationship in category.getElementsByTagName('Relationships'):
                    for has_member in relationship.getElementsByTagName('Has_Member'):
                        cwe_id = has_member.attributes['CWE_ID'].value
                        cwe_ids.append(f'CWE-{cwe_id}')
                mappings.append((year, f'A{i}', description, cwe_ids))
    return mappings


def filter_description(description):
    description = description.replace('Cross Site', 'Cross-Site')
    description = description.replace(' Flaws', '')
    description = description.replace('Forgery(CSRF)', 'Forgery (CSRF)')
    if description == 'Insecure Direct Object Reference':
        description = 'Insecure Direct Object References'
    if description == 'Broken Authentication':
        description = 'Broken Authentication and Session Management'
    return description


def get_owasp_description_dict(years=[2017, 2021]):
    description_dict = dict()
    invalid_keys = []
    for mapping in get_owasp_cwe_mappings(years):
        key = filter_description(mapping[2])
        value = (mapping[0], mapping[3])
        if key in description_dict:
            description_dict[key].append(value)
        else:
            description_dict[key] = [value]
    for key in description_dict:
        year_set = set()
        cwe_set = set()
        for year, cwes in description_dict[key]:
            year_set.add(year)
            cwe_set.update(cwes)
        description_dict[key] = (year_set, cwe_set)
        if len(cwe_set) == 0:
            invalid_keys.append(key)
    for key in invalid_keys:
        del description_dict[key]
    return description_dict


def get_owasp_cwe_dict(years=[2017, 2021]):
    cwe_dict = dict()
    for mapping in get_owasp_cwe_mappings(years):
        description = filter_description(mapping[2])
        for cwe in mapping[3]:
            if cwe in cwe_dict:
                cwe_dict[cwe].add(description)
            else:
                cwe_dict[cwe] = {description}
    return cwe_dict


def get_security_policy_matched_keywords(repo, keywords):
    matched_keywords = []
    content = get_latest_content(get_file_path(repo))
    content = content.lower()
    for keyword in keywords:
        keyword = keyword.lower()
        if keyword in content:
            matched_keywords.append(keyword)
    return matched_keywords


def get_keywords(s):
    pattern = r'\(([^)]*)\)'
    list_1 = list(filter(lambda x: len(x) > 0, re.sub(pattern, '', s).split(' ')))
    list_2 = re.findall(pattern, s)
    return [' '.join(list_1)] + list_2


def do_something(security_policy_repo):
    print(security_policy_repo)


if __name__ == '__main__':
    owasp_description_dict = get_owasp_description_dict([2004, 2007, 2010, 2013, 2017, 2021])
    keywords = []
    for key in owasp_description_dict:
        for keyword in get_keywords(key):
            keywords.append(keyword)
    matched_keywords = repos(get_security_policy_matched_keywords, keywords)

    _, repo_names = get_column_title_and_values(0)

    for repo, keywords in zip(repo_names, matched_keywords):
        if len(keywords) > 0:
            print(f'{repo},{keywords}')



    # for security_policy_repo in sss:
    #     print(f'{security_policy_repo} {sss[security_policy_repo]}')


    # for repo, desc, cwes in zip(repos, matched_keywords, repo_cwes):
    #     print(f'{repo} {desc} {cwes}')


    # _, values = get_column_title_and_values(29)
    # cwes = dummy_dummy(values)
    #
    # for key in owasp_descriptions:
    #     if owasp_descriptions[key] != [[]]:
    #         print(f'{key} {owasp_descriptions[key]} {cwes[key]}')


