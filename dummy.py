import os
from datetime import datetime

import numpy as np
import pandas as pd

import repository
import security_md
from document.document_attribute_download import get_saved_issue_list, repos
from document.document_categorisation_all import attribute_file_path
from utils import csv_reader, sort_by_descending_keys, sort_by_descending_values

security_related_keywords = ['access policy', 'access role', 'access-policy', 'access-role', 'accesspolicy', 'accessrole', 'aes', 'audit', 'authentic', 'authority', 'authoriz', 'biometric', 'black list', 'black-list', 'blacklist', 'blacklist', 'cbc', 'certificate', 'checksum', 'cipher', 'clearance', 'confidentiality', 'cookie', 'crc', 'credential', 'crypt', 'csrf', 'decode', 'defensive programming', 'defensive-programming', 'delegation', 'denial of service', 'denial-of-service', 'diffie-hellman', 'dmz', 'dotfuscator', 'dsa', 'ecdsa', 'encode', 'escrow', 'exploit', 'firewall', 'forge', 'forgery', 'gss api', 'gss-api', 'gssapi', 'hack', 'hash', 'hmac', 'honey pot', 'honey-pot', 'honeypot', 'inject', 'integrity', 'kerberos', 'ldap', 'login', 'malware', 'md5', 'nonce', 'nss', 'oauth', 'obfuscat', 'open auth', 'open-auth', 'openauth', 'openid', 'owasp', 'password', 'pbkdf2', 'pgp', 'phishing', 'pki', 'privacy', 'private key', 'private-key', 'privatekey', 'privilege', 'public key', 'public-key', 'publickey', 'rbac', 'rc4', 'repudiation', 'rfc 2898', 'rfc-2898', 'rfc2898', 'rijndael', 'rootkit', 'rsa', 'salt', 'saml', 'sanitiz', 'secur', 'sha', 'shell code', 'shell-code', 'shellcode', 'shibboleth', 'signature', 'signed', 'signing', 'sing sign-on', 'single sign on', 'single-sign-on', 'smart assembly', 'smart-assembly', 'smartassembly', 'snif', 'spam', 'spnego', 'spoofing', 'spyware', 'ssl', 'sso', 'steganography', 'tampering', 'trojan', 'trust', 'violat', 'virus', 'white list', 'white-list', 'whitelist', 'x509', 'xss']

issue_directory_path = 'C:\\Files\\issues\\'


def files_and_repos(directory_path, file_extension, function):
    for file_name in os.listdir(directory_path):
        repo = file_name.replace(f'.{file_extension}', '', -1).replace('_', '/', 1)
        function(directory_path, file_name, repo)


def get_issues_by_year(repo):
    issue_dict = dict()
    issue_file_name = repo.replace('/', '_')
    issue_file_path = f'{issue_directory_path}{issue_file_name}.txt'
    for issue in get_saved_issue_list(issue_file_path):
        created_at = issue['node']['createdAt']
        date_time = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        year = int(date_time.strftime('%Y'))
        if year in issue_dict:
            issue_dict[year].append(issue)
        else:
            issue_dict[year] = [issue]
    return issue_dict


def get_security_issue_count(issues):
    number_of_issues = len(issues)
    issue_types = np.zeros(number_of_issues)
    for i in range(number_of_issues):
        comments = issues[i]['node']['comments']['edges']
        number_of_comments = len(comments)
        comment_types = np.zeros(number_of_comments)
        for j in range(number_of_comments):
            for text in comments[j]['node']['bodyText'].split(' '):
                text_length = len(text)
                if text_length == 3:
                    for keyword in security_related_keywords:
                        if keyword == text:
                            comment_types[j] = 1
                            break
                elif text_length > 3:
                    for keyword in security_related_keywords:
                        if keyword in text:
                            comment_types[j] = 1
                            break
        if number_of_comments > 0 and len([x for x in comment_types if x == 1]) / number_of_comments > 0.5:
            issue_types[i] = 1
    return len([x for x in issue_types if x == 1])


def get_count_dict():
    count_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        if row[1] != 'failed':
            count = int(row[1])
        else:
            count = None
        if count is not None:
            count_dict[row[0]] = count
    return count_dict


def dummy_dummy():
    for file_name in os.listdir('C:\\Files\\a1\\'):
        repo = file_name.replace('.csv', '', -1).replace('_', '/', 1)
        issue_dict = get_issues_by_year(repo)
        for year in issue_dict.keys():
            issues = issue_dict[year]
            issue_dict[year] = (len(issues), get_security_issue_count(issues))
        for year in issue_dict.keys():
            print(f'{repo},{year},{issue_dict[year][0]},{issue_dict[year][1]}')


def ddd(directory_path, file_name, repo):
    count_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        if row[1] != 'failed':
            count = int(row[1])
        else:
            count = None
        if count is not None:
            count_dict[row[0]] = count
    with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
        issues = eval(f.readlines()[0])
        if repo in count_dict:
            count = count_dict[repo]
            if count > len(issues) and count < 5000:
                print(f'\'{repo}\',')
        # else:
        #     print(f'{file_name} None')

directory_path = 'C:\\Files\\issues\\'
file_extension = 'txt'

def value(k, d, default=None):
    if k in d:
        v = d[k]
    else:
        v = default
    return v


def get_issue_counts(repo):
    issue_dict = dict()
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.{file_extension}'
    for issue in get_saved_issue_list(f'{directory_path}{file_name}'):
        created_at = issue['node']['createdAt']
        date_time = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        year = int(date_time.strftime('%Y'))
        if year in issue_dict:
            issue_dict[year].append(issue)
        else:
            issue_dict[year] = [issue]
    return (
        repo,
        len(value(2018, issue_dict, [])),
        len(value(2019, issue_dict, [])),
        len(value(2020, issue_dict, [])),
        len(value(2021, issue_dict, [])),
        len(value(2022, issue_dict, []))
    )


def get_issue_counts_from_attribute_file():
    issue_counts = []
    i = 0
    for row in csv_reader(attribute_file_path):
        if i >= 2:
            issue_counts.append((
                row[0],
                int(row[14]),
                int(row[15]),
                int(row[16]),
                int(row[17]),
                int(row[18])
            ))
        i = i + 1
    return issue_counts


def c(i, j):
    return j != 0 and i >= j



    # files_and_repos(directory_path, 'txt', get_repo_issues)
    # files_and_repos(directory_path, file_extension, ddd)

    # issues = get_saved_issue_list(f'C:\\Files\\issues\\apollographql_apollo-client.txt')
    # print(len(issues))

    # count_dict = get_count_dict()
    #
    # for key in count_dict:
    #     count = count_dict[key]
    #     if count > 20000:
    #         print(f'{key} {count}')

    # rows = get_issue_counts_from_attribute_file()
    # for file_name in os.listdir('C:\\Files\\a1\\'):
    #     a_repo = file_name.replace('.csv', '', -1).replace('_', '/', 1)
    #     a = get_issue_counts(a_repo)
    #     a_repo, a_2018, a_2019, a_2020, a_2021, a_2022 = a
    #     for b in rows:
    #         b_repo, b_2018, b_2019, b_2020, b_2021, b_2022 = b
    #         if a_repo == b_repo:
    #             a_s = f'{a_2018}, {a_2019}, {a_2020}, {a_2021}, {a_2022}'
    #             b_s = f'{b_2018}, {b_2019}, {b_2020}, {b_2021}, {b_2022}'
    #             if a != b and a_2018 == 0 and a_2019 == 0 and a_2020 == 0 and a_2021 == 0 and a_2022 == 0:
    #                 print(f'{a_repo} | {a_s} | {b_s}')
    #             break


def get_user_dict():
    user_dict = dict()
    i = 0
    for row in csv_reader(attribute_file_path):
        if i >= 2:
            user = row[1]
            if user in user_dict:
                user_dict[user] = user_dict[user] + 1
            else:
                user_dict[user] = 1
        i = i + 1
    return user_dict

if __name__ == '__main__':
    # dummy_dummy()
    user_dict = get_user_dict()
    for user in sort_by_descending_values(user_dict):
        print(f'{user},{user_dict[user]}')