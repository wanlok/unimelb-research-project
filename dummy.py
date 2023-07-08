import os

import numpy as np
import pandas as pd

import repository
import security_md
from document.document_attribute_download import e_list
from utils import csv_reader

security_related_keywords = ['access policy', 'access role', 'access-policy', 'access-role', 'accesspolicy', 'accessrole', 'aes', 'audit', 'authentic', 'authority', 'authoriz', 'biometric', 'black list', 'black-list', 'blacklist', 'blacklist', 'cbc', 'certificate', 'checksum', 'cipher', 'clearance', 'confidentiality', 'cookie', 'crc', 'credential', 'crypt', 'csrf', 'decode', 'defensive programming', 'defensive-programming', 'delegation', 'denial of service', 'denial-of-service', 'diffie-hellman', 'dmz', 'dotfuscator', 'dsa', 'ecdsa', 'encode', 'escrow', 'exploit', 'firewall', 'forge', 'forgery', 'gss api', 'gss-api', 'gssapi', 'hack', 'hash', 'hmac', 'honey pot', 'honey-pot', 'honeypot', 'inject', 'integrity', 'kerberos', 'ldap', 'login', 'malware', 'md5', 'nonce', 'nss', 'oauth', 'obfuscat', 'open auth', 'open-auth', 'openauth', 'openid', 'owasp', 'password', 'pbkdf2', 'pgp', 'phishing', 'pki', 'privacy', 'private key', 'private-key', 'privatekey', 'privilege', 'public key', 'public-key', 'publickey', 'rbac', 'rc4', 'repudiation', 'rfc 2898', 'rfc-2898', 'rfc2898', 'rijndael', 'rootkit', 'rsa', 'salt', 'saml', 'sanitiz', 'secur', 'sha', 'shell code', 'shell-code', 'shellcode', 'shibboleth', 'signature', 'signed', 'signing', 'sing sign-on', 'single sign on', 'single-sign-on', 'smart assembly', 'smart-assembly', 'smartassembly', 'snif', 'spam', 'spnego', 'spoofing', 'spyware', 'ssl', 'sso', 'steganography', 'tampering', 'trojan', 'trust', 'violat', 'virus', 'white list', 'white-list', 'whitelist', 'x509', 'xss']


def files_and_repos(directory_path, file_extension, function):
    for file_name in os.listdir(directory_path):
        repo = file_name.replace(f'.{file_extension}', '', -1).replace('_', '/', 1)
        function(directory_path, file_name, repo)


def get_repo_issues(directory_path, file_name, repo):
    with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
        issues = eval(f.readlines()[0])
        number_of_issues = len(issues)
        issue_types = np.zeros(number_of_issues)
        for i in range(number_of_issues):
            created_at = issues[i]['node']['createdAt']
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
        print(f'{repo} {number_of_issues} {len([x for x in issue_types if x == 1]) }')


def ddd(directory_path, file_name, repo):
    count_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        repo = row[0]
        if row[1] != 'failed':
            count = int(row[1])
        else:
            count = None
        if count is not None:
            count_dict[repo] = count
    with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
        issues = eval(f.readlines()[0])
        if repo in count_dict:
            count = count_dict[repo]
            if count != len(issues) and count < 5000 and file_name in e_list:
                print(f'\'{file_name}\',')
        # else:
        #     print(f'{file_name} None')


if __name__ == '__main__':
    directory_path = 'C:\\Files\\issues\\'
    file_extension = 'txt'
    # files_and_repos(, 'txt', get_repo_issues)
    files_and_repos(directory_path, file_extension, ddd)