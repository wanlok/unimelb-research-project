import math
import os
import re

import pandas as pd
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import csv_reader


def is_type_1_header(line):
    return len(line) >= 2 and (line == len(line) * '=' or line == len(line) * '-')


def is_type_2_header(line):
    return line[:2].strip() == '#' or line[:2] == '##' and line[:3] != '###'


stop_words = set(stopwords.words('english'))
stop_words.update({'please', 'thank'})

lemmatizer = WordNetLemmatizer()
url_pattern = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
relative_link_pattern = r'\[(.*?)\]\((?!http)(?!#)(.*?)\)'
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
phone_number_pattern = r'\d+(?:-\d+)+'
cwe_number_pattern = r'CWE-\d+'
cve_number_pattern = r'CVE-\d{4}-\d+'
encryption_key_pattern = r'\b(?:[0-9A-Fa-f]{4}\s+){9}[0-9A-Fa-f]{4}\b'
pgp_key_pattern = r'-----BEGIN PGP PUBLIC KEY BLOCK-----.*?-----END PGP PUBLIC KEY BLOCK-----'


def dummy(content):
    content = content.lower()
    content = content.replace('node.js', 'nodejs')
    content = content.replace('tls/ssl', 'tlsssl')
    content = re.sub(r'[\u4e00-\u9fff]+', '', content)
    # content = re.sub(r'\W+', ' ', content)
    # content = [x for x in content.split(' ') if x not in stop_words]
    content = re.compile(r'[a-zA-Z_]+').findall(content)
    content = list(map(lambda x: lemmatizer.lemmatize(x, 'v'), content))
    content = [x for x in content if x not in stop_words]
    content = list(filter(lambda x: x.isnumeric() or len(x) > 1, content))
    content = ' '.join(content)
    return content


def extract_information(file_name, lines):
    content = ' '.join(lines)
    cwe_numbers = re.findall(cwe_number_pattern, content)
    for cwe_number in cwe_numbers:
        content = content.replace(cwe_number, '')
    cve_numbers = re.findall(cve_number_pattern, content)
    for cve_number in cve_numbers:
        content = content.replace(cve_number, '')
    relative_links = re.findall(relative_link_pattern, content)
    urls = re.findall(url_pattern, content)
    for url in urls:
        content = content.replace(url, '')
    emails = re.findall(email_pattern, content)
    for email in emails:
        content = content.replace(email, '')
    phone_numbers = re.findall(phone_number_pattern, content)
    for phone_number in phone_numbers:
        content = content.replace(phone_number, '')
    encryption_keys = re.findall(encryption_key_pattern, content) + re.findall(pgp_key_pattern, content)
    for encryption_key in encryption_keys:
        content = content.replace(encryption_key, '')
    return content, urls, relative_links, emails, phone_numbers, cwe_numbers, cve_numbers, encryption_keys


def perform(file_name, header, lines, my_list):
    line_content, line_urls, line_relative_links, line_emails, line_phone_numbers, line_cwe_numbers, line_cve_numbers, line_encryption_keys = extract_information(file_name, lines)
    lines.clear()
    if header is not None:
        header_content, header_urls, header_relative_links, header_emails, header_hone_numbers, header_cwe_numbers, header_cve_numbers, header_encryption_keys = extract_information(file_name, [header])
        urls = header_urls + line_urls
        relative_links = header_relative_links + line_relative_links
        emails = header_emails + line_emails
        phone_numbers = header_hone_numbers + line_phone_numbers
        cwe_numbers = header_cwe_numbers + line_cwe_numbers
        cve_numbers = header_cve_numbers + line_cve_numbers
        encryption_keys = header_encryption_keys + line_encryption_keys
        my_list.append((file_name, dummy(header_content), dummy(line_content), relative_links, urls, emails, phone_numbers, cwe_numbers, cve_numbers, encryption_keys))


def is_substring(features, strings):
    valid = False
    for feature in features:
        for string in strings:
            if string in feature:
                valid = True
                break
    return valid


def classify(t, features):
    categories = []
    header = t[1].split(' ')
    disclosure_policy_list = ['publish', 'cve', 'privacy', 'disclosure', 'process', 'reply', 'public', 'notification', 'confidential', 'embargo', 'transparent', 'transparency']
    if is_substring(header, disclosure_policy_list) or is_substring(features, disclosure_policy_list):
        categories.append('disclosure policy')
    reporting_procedure_list = ['report', 'instruction', 'suggestion', 'reward', 'program', 'presence', 'via', 'new', 'language', 'sentence', 'obtain', 'propose'] # [, 'reward', 'bonus', 'response', 'privacy', 'confidential']):
    if is_substring(header, reporting_procedure_list) or is_substring(features, reporting_procedure_list):
        categories.append('reporting procedure')
    contact_information_list = ['reach', 'contact']
    if is_substring(header, contact_information_list) or is_substring(features, contact_information_list) or len(t[4]) > 0 or len(t[5]) > 0 or len(t[6]) > 0:
        categories.append('contact information')
    # elif is_substring(s, ['past', 'known', 'advisories', 'history', 'audits']):
    if len(t[7]) > 0 or len(t[8]) > 0:
        categories.append('past issues')
    support_version_list = ['support', 'version', 'white_check_mark', 'discontinue', 'major', 'release']
    if is_substring(header, support_version_list) or is_substring(features, support_version_list):
        categories.append('supported versions')
    # elif is_substring(s, ['encrypt', 'key', 'pgp']):
    #     key = 'encryption'
    if len(t[9]) > 0:
        categories.append('encryption')
    eligibility_list = ['lfd', 'xxe', 'ssrf', 'rce', 'xml', 'cookie', 'session', 'sql', 'eligible', 'verified',
                        'exclusion', 'scope', 'party', 'javascript', 'false', 'cipher', 'model', 'plugins',
                        'responsibility', 'static', 'inadvertent', 'relate', 'constitute']
    if is_substring(header, eligibility_list) or is_substring(features, eligibility_list):
        categories.append('eligibility')
    instruction_list = ['truststore', 'practice', 'classification', 'project', 'design']
    if is_substring(header, instruction_list) or is_substring(features, instruction_list):
        categories.append('instruction')
    other_list = ['asrc', 'preface', 'prologue', 'securely', 'principle', 'convention']
    if is_substring(features, other_list) or 'security policy' in t[1] or len(features) <= 4:
        categories.append('others')

    # if is_substring(s, ['disclosure', 'reward', 'bonus', 'response', 'privacy', 'confidential']):
    if len(categories) == 0 and len(t[3]) > 0:
        for relative_link in t[3]:
            if 'security.md' in relative_link[1].lower():
                categories.append('referral')
    return categories


if __name__ == '__main__':
    directory_path = 'C:\\Files\\a\\'
    my_list = []
    for file_name in os.listdir(directory_path):
        row = None
        i = 0
        for r in csv_reader(f'{directory_path}{file_name}'):
            if i > 0:
                row = r
            i = i + 1
        if row is not None:
            previous_line = None
            header = None
            lines = []
            for line in row[5].split('\n'):
                if is_type_1_header(line) and previous_line is not None and len(previous_line) > 0:
                    perform(file_name, header, lines, my_list)
                    header = previous_line
                elif is_type_2_header(line):
                    perform(file_name, header, lines, my_list)
                    header = line.replace('#', '')
                else:
                    lines.append(line)
                previous_line = line
            perform(file_name, header, lines, my_list)

    texts = list(map(lambda x: f'{x[1]} {x[2]}'.strip(), my_list))
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Convert the matrix to a dense array
    # feature_vectors = tfidf_matrix.toarray()

    # Print the feature vectors
    # print(vectorizer.get_feature_names_out())
    # print(feature_vectors)

    # Convert the TF-IDF matrix to a pandas DataFrame
    df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    pool = 10
    count_1 = 0
    count_2 = 0

    for i in range(len(my_list)):
        t = my_list[i]
        a_list = []
        for j, word in enumerate(df.columns):
            tfidf = df.loc[i, word]
            if tfidf > 0:
                a_list.append((word, tfidf))
        content = f'{t[1]} {t[2]}'.strip()
        features = list(map(lambda x: x[0], sorted(a_list, key=lambda x: -x[1])))[:12]
        categories = classify(t, features)
        should_display = True
        if len(categories) > 0:
            count_1 = count_1 + 1
            should_display = False
        count_2 = count_2 + 1
        if should_display:
            print(f'FILE_NAME       : {t[0]}')
            print(f'HEADER          : {t[1]}')
            print(f'CONTENT         : {content}')
            print(f'FEATURES        : {features}')
            print(f'RELATIVE_LINKS  : {t[3]}')
            print(f'URLS            : {t[4]}')
            print(f'EMAILS          : {t[5]}')
            print(f'PHONE_NUMBERS   : {t[6]}')
            print(f'CWE_NUMBERS     : {t[7]}')
            print(f'CVE_NUMBERS     : {t[8]}')
            print(f'ENCRYPTION KEYS : {t[9]}')
            print(f'CATEGORIES      : {categories}')
            print()
        # if count_2 - count_1 == pool:
            # break

    print(f'{count_1} / {count_2}')


