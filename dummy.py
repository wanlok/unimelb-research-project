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


def get_yearly_security_issue_counts(repo):
    issue_dict = get_issues_by_year(repo)
    for year in issue_dict.keys():
        issues = issue_dict[year]
        issue_dict[year] = (len(issues), get_security_issue_counts(issues))
    for year in issue_dict.keys():
        counts = ','.join(map(lambda x: f'{int(x)}', issue_dict[year][1]))
        print(f'{repo},{year},{issue_dict[year][0]},{counts}')


def get_issues_and_security_issues_by_year(repo, year):
    issues = []
    security_related_issues = []
    issue_dict = get_issues_by_year(repo)
    if year in issue_dict and len(issue_dict[year]) > 0:
        issues = issue_dict[year]
        for issue in issues:
            title = issue['node']['title']
            body_text = issue['node']['bodyText']
            if is_security_related_text(title) or is_security_related_text(body_text):
                security_related_issues.append(issue)
    return issues, security_related_issues


def extract_security_related_keywords(text):
    keywords = set()
    words = list(map(lambda x: x.lower(), text.split(' ')))
    for keyword in security_related_keywords:
        keyword = keyword.lower()
        keyword_length = len(keyword)
        for i in range(len(words)):
            word = words[i]
            if (keyword_length == 3 and keyword == word) or (keyword_length > 3 and keyword in word):
                keywords.add(keyword)
            else:
                slices = keyword.split(' ')
                words_with_spaces = words[i:i + len(slices)]
                if slices == words_with_spaces:
                    keywords.add(' '.join(words_with_spaces))
    return keywords


def is_security_related_text(text):
    security_related = False
    words = list(map(lambda x: x.lower(), text.split(' ')))
    for keyword in security_related_keywords:
        keyword = keyword.lower()
        keyword_length = len(keyword)
        for i in range(len(words)):
            word = words[i]
            if (keyword_length == 3 and keyword == word) or (keyword_length > 3 and keyword in word):
                security_related = True
                break
            else:
                slices = keyword.split(' ')
                if slices == words[i:i + len(slices)]:
                    security_related = True
                    break
        if security_related:
            break
    return security_related


def get_security_related_ratios(issue):
    title = issue['title']
    title_security_related = 1 if is_security_related_text(title) else 0
    body_text = issue['bodyText']
    body_text_security_related = 1 if is_security_related_text(body_text) else 0
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

    if title_security_related or body_text_security_related:
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


def value(k, d, default=None):
    if k in d:
        v = d[k]
    else:
        v = default
    return v


def get_issue_counts(repo):
    issue_dict = dict()
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    for issue in get_saved_issue_list(f'{issue_directory_path}{file_name}'):
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
    # return j != 0 and i >= j
    # return i >= j or j == 0
    return i == j

    # files_and_repos(directory_path, 'txt', get_repo_issues)
    # files_and_repos(directory_path, file_extension, ddd)


def get_mismatch():
    # issues = get_saved_issue_list(f'C:\\Files\\issues\\apollographql_apollo-client.txt')
    # print(len(issues))
    rows = get_issue_counts_from_attribute_file()
    for file_name in os.listdir('C:\\Files\\security policies\\'):
        a_repo = file_name.replace('.csv', '', -1).replace('_', '/', 1)
        a = get_issue_counts(a_repo)
        a_repo, a_2018, a_2019, a_2020, a_2021, a_2022 = a
        for b in rows:
            b_repo, b_2018, b_2019, b_2020, b_2021, b_2022 = b
            if a_repo == b_repo:
                a_s = f'{a_2018}, {a_2019}, {a_2020}, {a_2021}, {a_2022}'
                b_s = f'{b_2018}, {b_2019}, {b_2020}, {b_2021}, {b_2022}'
                # if a != b:
                if c(a_2018, b_2018) and c(a_2019, b_2019) and c(a_2020, b_2020) and c(a_2021, b_2021) and c(a_2022, b_2022):
                    pass
                else:
                    print(f'{a_repo} | {a_s} | {b_s}')
                break


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


def count_merger():
    new_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\r\\repo_issue_counts.txt'):
        new_dict[row[0]] = row[1]
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        repo, count = row
        if repo in new_dict:
            count = new_dict[repo]
        print(f'{repo},{count}')


def get_project_dict():
    project_dict = dict()
    i = 0
    for row in csv_reader(attribute_file_path):
        if i >= 2:
            repo = row[0]
            project = repo.split('/')[1]
            if project in project_dict:
                project_dict[project].append(repo)
            else:
                project_dict[project] = [repo]
        i = i + 1
    return project_dict



def get_number_of_words_headers_paragraphs(repo):
    content = get_latest_content(get_file_path(repo))
    words = list(filter(lambda x: is_contain_alphanumeric(x), content.replace('\n', ' ').split(' ')))
    headers, paragraphs = get_headers_and_paragraphs(content)
    distinct_headers = []
    previous = None
    for header in headers:
        if header != previous:
            distinct_headers.append(header)
        previous = header
    return repo, len(words), len(distinct_headers), len(paragraphs)


def aaa():
    i = 0
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\20230720 user_repo.csv'):
        if i > 0:
            user = row[0]
            number_of_projects = int(row[1])
            number_of_unique_documents = int(row[2])
            distribution = list(map(lambda x: int(x), eval(row[4])))
            number_of_similar_documents = int(row[5])
            eighty_percent_list = list(map(lambda x: float(x), eval(row[6])))
            eighty_percent_count = int(row[7])
            if number_of_projects != number_of_unique_documents:
                print(f'{user},{eighty_percent_count}')
                # print(f'{user},{number_of_projects},{number_of_unique_documents},{distribution},{number_of_similar_documents},{eighty_percent_list},{eighty_percent_count}')
        i = i + 1


def dumm2():
    my_list = []
    file = open(f'C:\\Users\\WAN Tung Lok\\Desktop\\repo_issues.txt', 'r')
    for line in file.readlines():
        slices = list(map(lambda x: x.strip(), line.split('|')))
        repo = slices[0]
        obtained_number_of_issues = list(map(lambda x: int(x.strip()), slices[1].split(',')))
        obtained_number_of_issues_all_zeros = set(obtained_number_of_issues) == {0}
        expected_number_of_issues = list(map(lambda x: int(x.strip()), slices[2].split(',')))
        expected_number_of_issues_all_zeros = set(expected_number_of_issues) == {0}
        acceptable = True
        for i in range(len(expected_number_of_issues)):
            x = obtained_number_of_issues[i]
            y = expected_number_of_issues[i]
            if abs(x - y) > 5:
                acceptable = False
                break
        # if acceptable and not obtained_number_of_issues_all_zeros:
        # if not acceptable and expected_number_of_issues_all_zeros:
        if obtained_number_of_issues_all_zeros:
            my_list.append((repo, obtained_number_of_issues, expected_number_of_issues))
    return my_list


def print_security_issue_title_titles_and_body_texts(repo_list):
    for repo, year in repo_list:
        issues, security_related_issues = get_issues_and_security_issues_by_year(repo, year)
        for security_related_issue in security_related_issues:
            title = security_related_issue['node']['title']
            body_text = security_related_issue['node']['bodyText']
            print(f'TITLE: {extract_security_related_keywords(title)} {[title]}')
            print(f'BODY TEXT: {extract_security_related_keywords(body_text)} {[body_text]}')
            print()
        print(f'{len(issues)} {len(security_related_issues)}')


if __name__ == '__main__':
    # rr = ['dotnet/efcore']

    # print_security_issue_title_titles_and_body_texts([('scipy/scipy', 2014)])
    repos(get_yearly_security_issue_counts)


    # texts = [
    #     'Hi there,\nI am having difficulties to track this issue down and I did search for a solution for like 2 days, even digging in the EF Core code did not help.\nI have a multi-tenant DB setup where each tenant has a separate DB. Therefore I need to attach the tenant ID to the context. The example linked in the Managing state in pooled contexts documentation perfectly fits my needs BUT ... I need to resolve the MyDbContext consecutively in a for loop to iterate over all tenant DBs like\nforeach (var tenantId in tenantIds)\n{\n   ...\n    \n    using (var context = serviceProvider.GetRequiredService<MyDbContext>())\n    {\n        ...\n    }\n}\nand this throws a\nSystem.ObjectDisposedException: Cannot access a disposed context instance. A common cause of this error is disposing a context instance that was resolved from dependency injection and then later trying to use the same context instance elsewhere in your application. This may occur if you are calling \'Dispose\' on the context instance, or wrapping it in a using statement. If you are using dependency injection, you should let the dependency injection container take care of disposing context instances.\nObject name: \'WeatherForecastContext\'.\n   at Microsoft.EntityFrameworkCore.DbContext.CheckDisposed()\n   at Microsoft.EntityFrameworkCore.DbContext.get_Database()\n\nas soon as I resolve MyDbContext a second time.\nYou can repro this by extending the WeatherForecastController from the aforementioned example with\n[HttpPost(Name = "GetWeatherForecast")]\npublic async Task<IEnumerable<WeatherForecast>> Post()\n{\n    using (var context1 = _services.GetRequiredService<WeatherForecastContext>())\n    {\n        await context1.Database.EnsureCreatedAsync();\n    }\n\n    using (var context2 = _services.GetRequiredService<WeatherForecastContext>())\n    {\n        await context2.Database.EnsureCreatedAsync();\n    }\n\n    return null;\n}\n... then start the application and run the action. It will fail with the same error as mentioned above.\nNow the strange part: when I use AddDbContextPool instead of AddPooledDbContextFactory in my application everything works flawlessly ... but with AddDbContextPool I cannot  attach state to MyDbContext.\nI think it has something to do with the scoped lease stuff, somehow this works differently when using the factory approach.\nSo I am a bit lost now as simply not disposing MyDbContext is not an option, right?\nIs there something missing that I need to do to make resolving in consecutive order possible?\nProvider and version information\nEF Core version: 6.0.1\nDatabase provider: Microsoft.EntityFrameworkCore.SqlServer\nTarget framework: .NET 6.0\nOperating system: Windows 11\nIDE: VS 2022 Version 17.3.0 Preview 5.0',
    #     'Way to omit discriminant with multiple classes(with identical properties) sharing a table',
    #     'I think there is a problem in the current SSL setting'
    # ]
    #
    # for body_text in texts:
    #     print([body_text])
    #     print(extract_security_related_keywords(body_text))

        # for i in range(10):
        #     print(issues[i])

    # get_mismatch()
    # project_dict = get_project_dict()
    # for project in project_dict:
    #     if len(project_dict[project]) > 1:
    #         print(f'{project_dict[project]}')




    # my_list = dumm2()
    # for a in my_list:
    #     print(f'{a[0]},{sum(a[2])}')


    # print(len(my_list))

    # i = 0
    # for row in csv_reader(attribute_file_path):
    #     if i > 1:
    #         target = None
    #         for a in my_list:
    #             if a[0] == row[0]:
    #                 target = a
    #         if target is None:
    #             print(f'{row[0]},{row[14]},{row[15]},{row[16]},{row[17]},{row[18]}')
    #         else:
    #             print(f'{target[0]},{target[1][0]},{target[1][1]},{target[1][2]},{target[1][3]},{target[1][4]}')
    #     i = i + 1

    # dumm()

    # x_values, y_values, title, x_title, y_title, file_path
    # scatter_plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 'Hello', 'x title', 'y title', 'C:\\Files\\aaa.png')

    # df = pd.DataFrame([[1., 2.], [3., 4.]], columns=['A', 'B'])
    # df2 = pd.DataFrame([[5., 10.]], columns=['A', 'B'])
    #
    # print(df)
    # print(df2)
    # print(df.div(df2))


    # print(is_filtered_word('Wi-'))

    # result_list = repos(get_number_of_words_headers_paragraphs)
    # for repo, number_of_words, number_of_headers, number_of_paragraphs in result_list:
    #     print(f'{repo},{number_of_words},{number_of_headers},{number_of_paragraphs}')

    # repo_names = [
    #     'google',
    # ]
    #
    # for name in repo_names:
    #     dummy_dummy(100, name)

    # aaa()
