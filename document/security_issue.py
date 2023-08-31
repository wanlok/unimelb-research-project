import os
from datetime import datetime

import numpy as np
import pandas as pd
from Levenshtein import distance

import repository
import security_md
from chart import scatter_plot
from document.document_attribute_download import get_saved_issue_list, repos
from document.document_categorisation_all import attribute_file_path
from document.document_classification import dummy_dummy
from document.document_utils import get_headers_and_paragraphs
from utils import csv_reader, sort_by_descending_keys, sort_by_descending_values, get_file_path, get_latest_content, \
    is_contain_alphanumeric

security_related_keywords = ['access policy', 'access role', 'access-policy', 'access-role', 'accesspolicy', 'accessrole', 'aes', 'audit', 'authentic', 'authority', 'authoriz', 'biometric', 'black list', 'black-list', 'blacklist', 'blacklist', 'cbc', 'certificate', 'checksum', 'cipher', 'clearance', 'confidentiality', 'cookie', 'crc', 'credential', 'crypt', 'csrf', 'decode', 'defensive programming', 'defensive-programming', 'delegation', 'denial of service', 'denial-of-service', 'diffie-hellman', 'dmz', 'dotfuscator', 'dsa', 'ecdsa', 'encode', 'escrow', 'exploit', 'firewall', 'forge', 'forgery', 'gss api', 'gss-api', 'gssapi', 'hack', 'hash', 'hmac', 'honey pot', 'honey-pot', 'honeypot', 'inject', 'integrity', 'kerberos', 'ldap', 'login', 'malware', 'md5', 'nonce', 'nss', 'oauth', 'obfuscat', 'open auth', 'open-auth', 'openauth', 'openid', 'owasp', 'password', 'pbkdf2', 'pgp', 'phishing', 'pki', 'privacy', 'private key', 'private-key', 'privatekey', 'privilege', 'public key', 'public-key', 'publickey', 'rbac', 'rc4', 'repudiation', 'rfc 2898', 'rfc-2898', 'rfc2898', 'rijndael', 'rootkit', 'rsa', 'salt', 'saml', 'sanitiz', 'secur', 'sha', 'shell code', 'shell-code', 'shellcode', 'shibboleth', 'signature', 'signed', 'signing', 'sing sign-on', 'single sign on', 'single-sign-on', 'smart assembly', 'smart-assembly', 'smartassembly', 'snif', 'spam', 'spnego', 'spoofing', 'spyware', 'ssl', 'sso', 'steganography', 'tampering', 'trojan', 'trust', 'violat', 'virus', 'white list', 'white-list', 'whitelist', 'x509', 'xss']

issue_directory_path = 'C:\\Files\\issues\\'


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


def get_issues_by_year_month(repo):
    issue_dict = dict()
    issue_file_name = repo.replace('/', '_')
    issue_file_path = f'{issue_directory_path}{issue_file_name}.txt'
    for issue in get_saved_issue_list(issue_file_path):
        created_at = issue['node']['createdAt']
        date_time = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        year = int(date_time.strftime('%Y'))
        month = int(date_time.strftime('%m'))
        month = '{:02d}'.format(month)
        year_month = f'{year}{month}'
        if year_month in issue_dict:
            issue_dict[year_month].append(issue)
        else:
            issue_dict[year_month] = [issue]
    return issue_dict


def get_yearly_security_issue_counts(repo, text_file):
    issue_dict = get_issues_by_year(repo)
    # issue_dict = get_issues_by_year_month(repo)
    for year in issue_dict.keys():
        issues = issue_dict[year]
        issue_dict[year] = (len(issues), get_security_issue_counts(issues))
    for year in issue_dict.keys():
        counts = ','.join(map(lambda x: f'{int(x)}', issue_dict[year][1]))
        print(f'{repo},{year},{issue_dict[year][0]},{counts}')
        text_file.write(f'{repo},{year},{issue_dict[year][0]},{counts}\n')


def get_issues_and_security_issues_by_year(repo, year):
    issues = []
    security_related_issues = []
    issue_dict = get_issues_by_year(repo)
    if year in issue_dict and len(issue_dict[year]) > 0:
        issues = issue_dict[year]
        for issue in issues:
            title = issue['node']['title']
            title_security_related_strings = get_security_related_strings(title)
            body_text = issue['node']['bodyText']
            body_text_security_related_strings = get_security_related_strings(body_text)
            if len(title_security_related_strings) > 0 or len(body_text_security_related_strings) > 0:
                security_related_issues.append((issue, title, title_security_related_strings, body_text, body_text_security_related_strings))
    return issues, security_related_issues


def get_security_related_strings(text):
    security_related_strings = set()
    keywords = list(map(lambda x: x.lower(), security_related_keywords))
    three_length_keywords = list(filter(lambda x: len(x) == 3, keywords))
    words = list(map(lambda x: x.lower(), text.split(' ')))
    security_related_strings.update([word for word in words if word in three_length_keywords])
    for keyword in [keyword for keyword in keywords if keyword not in three_length_keywords]:
        if keyword in text:
            security_related_strings.add(keyword)
    return security_related_strings


def get_security_related_ratios(issue):
    title = issue['title']
    title_security_related_strings = get_security_related_strings(title)
    body_text = issue['bodyText']
    body_text_security_related_strings = get_security_related_strings(body_text)
    # comments = issue['comments']['edges']
    # number_of_comments = len(comments)
    # comments_security_related = [0] * number_of_comments
    # for i in range(number_of_comments):
    #     if is_security_related_text(comments[i]['node']['bodyText']):
    #         comments_security_related[i] = 1
    # if title_security_related or body_text_security_related:
    #     security_related_ratios = [0] * 10
    # else:
    #     security_related_ratios = [0] * 10
    # if number_of_comments > 0:
    #     percentage = len([x for x in comments_security_related if x == 1]) / number_of_comments
    #     for i in range(10):
    #         if percentage >= (i + 1) * 0.1: # 10% 20% 30% ... 100%
    #             security_related_ratios[i] = 1

    if len(title_security_related_strings) > 0 or len(body_text_security_related_strings) > 0:
        security_related_ratios = [1]
    else:
        security_related_ratios = [0]
    return security_related_ratios


def get_security_issue_counts(issues):
    security_issue_counts = []
    number_of_issues = len(issues)
    for i in range(number_of_issues):
        security_issue_counts.append(get_security_related_ratios(issues[i]['node']))
    df = pd.DataFrame(security_issue_counts)
    return df.sum(axis=0).tolist()


def print_security_issue_title_titles_and_body_texts(repo_list):
    for repo, year in repo_list:
        issues, security_related_issues = get_issues_and_security_issues_by_year(repo, year)
        for _, title, title_security_related_strings, body_text, body_text_security_related_strings in security_related_issues:
            print(f'TITLE: {title_security_related_strings} {[title]}')
            print(f'BODY TEXT: {body_text_security_related_strings} {[body_text]}')
            print()
        print(f'{len(issues)} {len(security_related_issues)}')


def ddd(repo, repo_set):
    repo_set.add(repo)


def aaa(repo, repo_dict):
    if repo in repo_dict:
        year_dict = repo_dict[repo]
        issue_counts = []
        security_issue_counts = []
        if '2018' in year_dict:
            issue_count, security_issue_count = year_dict['2018']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        if '2019' in year_dict:
            issue_count, security_issue_count = year_dict['2019']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        if '2020' in year_dict:
            issue_count, security_issue_count = year_dict['2020']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        if '2021' in year_dict:
            issue_count, security_issue_count = year_dict['2021']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        if '2022' in year_dict:
            issue_count, security_issue_count = year_dict['2022']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        if '2023' in year_dict:
            issue_count, security_issue_count = year_dict['2023']
            issue_counts.append(issue_count)
            security_issue_counts.append(security_issue_count)
        else:
            issue_counts.append(0)
            security_issue_counts.append(0)
        i = ','.join(map(lambda x: f'{x}', issue_counts))
        j = ','.join(map(lambda x: f'{x}', security_issue_counts))
        print(f'{repo},{i},{j}')
    else:
        print(f'{repo},0,0,0,0,0,0,0,0,0,0,0,0')



def process_issues():
    file_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\security-related issues\\main.csv'
    repo_dict = dict()
    for row in csv_reader(file_path):
        repo, year_month, issue_count, security_issue_count = row
        issue_count = int(issue_count)
        security_issue_count = int(security_issue_count)
        year = year_month[0:4]
        if repo in repo_dict:
            year_dict = repo_dict[repo]
            if year in year_dict:
                issue_total, security_issue_total = year_dict[year]
                year_dict[year] = (issue_total + issue_count, security_issue_total + security_issue_count)
            else:
                year_dict[year] = (issue_count, security_issue_count)
        else:
            repo_dict[repo] = dict()
            repo_dict[repo][year] = (issue_count, security_issue_count)
    repos(aaa, repo_dict)


if __name__ == '__main__':
    # print_security_issue_title_titles_and_body_texts([('tensorflow/tensorflow', 2020)])

    text_file = open('C:\\Files\\abc.txt', 'w', encoding='utf-8')
    repos(get_yearly_security_issue_counts, text_file)
    text_file.close()