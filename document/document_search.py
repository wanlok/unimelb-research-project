import os
import re
import sys

from document.owasp import get_owasp_cwe_mappings

sys.path.append('C:\\Files\\Projects\\unimelb-research-project')

from utils import contain_string, get_latest_content, csv_reader

from docx import Document

from document_utils import get_lines, directory_paths, ignored_file_names, get_categories, get_headers_and_paragraphs

def aaa():
    # text = 'take the security of our software products and services seriously'
    # text = 'consider vulnerabilities leading to the compromise'
    # text = 'threat model'
    # text = 'process is to reduce the total time users are vulnerable to publicly known exploits'
    if len(sys.argv) > 2:
        mode = int(sys.argv[1])
        text = ' '.join(sys.argv[2:])
        file_number = 0
        for directory_path in directory_paths:
            for file_name in os.listdir(directory_path):
                if file_name not in ignored_file_names:
                    file_path = f'{directory_path}{file_name}'
                    f = open(file_path, 'rb')
                    table = Document(f).tables[0]
                    category_lines = get_lines(table, 0)
                    content_lines = get_lines(table, 1)
                    if mode == 0 and text.lower() in category_lines.lower():
                        file_number = file_number + 1
                        print(f'{file_number} {file_path}')
                    elif mode == 1 and text.lower() in content_lines.lower():
                        file_number = file_number + 1
                        print(f'{file_number} {file_path}')
                    else:
                        categories = get_categories(category_lines)
                        headers, paragraphs = get_headers_and_paragraphs(content_lines)
                        if mode == 2:
                            for i in range(len(categories)):
                                if contain_string(text, categories[i], True) and len(categories[i]) == 1:
                                    file_number = file_number + 1
                                    print(f'{file_number} {file_path} {categories[i]}')
                        elif mode == 3:
                            found = False
                            for i in range(len(paragraphs)):
                                if text.lower() in paragraphs[i].lower():
                                    found = True
                                    break
                            if found:
                                file_number = file_number + 1
                                print(f'{file_number} {file_path} {categories[i]}')

                        elif mode == 4:
                            found = False
                            for i in range(len(categories)):
                                first = False
                                paragraph = paragraphs[i]
                                for j in range(len(categories[i])):
                                    if text.lower() in categories[i][j].lower():
                                        if len(categories[i]) > 1:
                                            print(f'{file_path} {categories[i]}')
                                        # print()
                                        # print(f'{header}')
                                        # print(f'{paragraph}')
                                        # print()
                                        found = True
                                        # break
                            # if found:
                            #     file_number = file_number + 1
                            #     print(f'{file_number} {file_path}')

                    f.close()


if __name__ == '__main__':
    keyword = 'cve'
    directory_path = 'C:\\Files\\security policies\\'

    owaps = [
        'Injection',
        'Broken Authentication',
        'Sensitive Data Exposure',
        'XML External Entities (XXE)',
        'Broken Access Control',
        'Security Misconfiguration',
        'Cross-Site Scripting (XSS)',
        'Insecure Deserialization'
        'Using Components with Known Vulnerabilities',
        'Insufficient Logging & Monitoring',
        'Broken Access Control',
        'Cryptographic Failures',
        'Injection',
        'Insecure Design',
        'Security Misconfiguration',
        'Vulnerable and Outdated Components',
        'Identification and Authentication Failures',
        'Software and Data Integrity Failures',
        'Security Logging and Monitoring Failures',
        'Server Side Request Forgery (SSRF)'
        'XML External Entities',
        'XXE',
        'Cross-Site Scripting',
        'Cross Site Scripting'
        'XSS',
        'Server Side Request Forgery',
        'SSRF'
    ]

    file_category_dict = dict()
    i = 0
    for row in csv_reader('C:\\Users\\Robert Wan\\Desktop\\Attributes.csv'):
        if i > 1:
            repo = row[0]
            file_name = repo.replace('/', '_')
            file_name = f'{file_name}.csv'
            if len(row[2]) > 0:
                categories = list(filter(lambda x: len(x) > 0, eval(row[2]).keys()))
            else:
                categories = []
            file_category_dict[file_name] = categories
        i = i + 1



    cve_set = set()
    for file_name in os.listdir(directory_path):
        for row in csv_reader(f'{directory_path}{file_name}'):
            date_time_string = row[3]
            # previous_content = row[4]
            content = row[5]
            # cwe = re.findall(r'\bCWE-\d+\b', content.lower())
            # owaps_contained = []
            # for o in owaps:
            #     if o.lower() in content.lower():
            #         owaps_contained.append(o)
            # if len(owaps_contained) > 0:
            #     print(f'{file_name} {date_time_string} {owaps_contained}')
            #     break

            # cves = re.findall(r'\bcve-\d{4}-\d{4,7}\b', content.lower())
            # if len(cves) > 0:
            #     # print(f'{file_name} {date_time_string} {cves}')
            #     cve_set.update(cves)

            if 'cve-' in content.lower():
                print(f'{file_name} {file_category_dict[file_name]} {date_time_string}')



    # cve_dict = dict()
    # for row in csv_reader('C:\\Files\\Projects\\nvdcve\\combine.csv'):
    #     cve_dict[row[0].lower()] = row[6]
    #
    # owasp_cwe_mappings = get_owasp_cwe_mappings([2017, 2021])
    #
    # print(owasp_cwe_mappings)
    #
    # owasp_dict = dict()
    #
    # # print(cve_set)
    # for cve in cve_set:
    #     if cve in cve_dict:
    #         for cwe in eval(cve_dict[cve]):
    #             owasp_description = None
    #             for _, _, description, cwe_list in owasp_cwe_mappings:
    #                 if cwe in cwe_list:
    #                     owasp_description = description
    #             if owasp_description in owasp_dict:
    #                 owasp_dict[owasp_description].add(cve)
    #             else:
    #                 owasp_dict[owasp_description] = {cve}
    #         # if keyword.lower() in content.lower():
    #         #     print(f'{file_name} {date_time_string}')
    #
    # for owasp_description in owasp_dict:
    #     print(f'{owasp_description} {len(owasp_dict[owasp_description])} {owasp_dict[owasp_description]}')
