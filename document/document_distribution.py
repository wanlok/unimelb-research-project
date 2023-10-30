from document.document_utils import category_names
from utils import csv_reader, sort_by_descending_values


def get_attribute_rows():
    rows = []
    i = 0
    for row in csv_reader('C:\\Users\\Robert Wan\\Desktop\\Attributes.csv'):
        if i > 1:
            rows.append(row)
        i = i + 1
    return rows


def get_top_10_security_policy_category_and_primary_language_distribution():
    my_dict = dict()
    for row in get_attribute_rows():
        security_policy_categories = eval(row[2])
        primary_language = row[45]
        for security_policy_category in security_policy_categories:
            key = f'{security_policy_category},{primary_language}'
            if key in my_dict:
                my_dict[key] = my_dict[key] + 1
            else:
                my_dict[key] = 1

    my_dict = sort_by_descending_values(my_dict)
    category_languages = []
    for category_name in category_names:
        languages = []
        for key in my_dict:
            slices = key.split(',')
            if category_name == slices[0]:
                languages.append(f'"{slices[1]}, {my_dict[key]}"')
        category_languages.append(languages)


    for i in range(len(category_names)):
        languages = ','.join(category_languages[i][:10])
        print(f'{chr(65 + i)},{languages}')


    # print(','.join(category_names))
    # for row in list(zip(*columns)):
    #     row = list(map(lambda x: f'{x}', row))
    #     print(','.join(row))


def get_application_domain_distribution():
    application_domain_dict = dict()
    for row in get_attribute_rows():
        application_domain = row[30]
        if application_domain in application_domain_dict:
            application_domain_dict[application_domain] = application_domain_dict[application_domain] + 1
        else:
            application_domain_dict[application_domain] = 1
    for application_domain in application_domain_dict:
        print(f'"{application_domain}",{application_domain_dict[application_domain]}')



def get_application_domains_and_security_policy_category():
    my_dict = dict()
    application_domains = set()
    for row in get_attribute_rows():
        security_policy_categories = eval(row[2])
        application_domain = row[30]
        if len(application_domain) > 0:
            application_domains.add(application_domain)
            for security_policy_category in security_policy_categories:
                key = f'{security_policy_category},{application_domain}'
                if key in my_dict:
                    my_dict[key] = my_dict[key] + 1
                else:
                    my_dict[key] = 1
    print(my_dict)
    application_domains = list(application_domains)
    application_domains.sort()
    a = ','.join(application_domains)
    print(f',{a}')
    for category_name in category_names:
        aaa = []
        for application_domain in application_domains:
            for key in my_dict:
                if key == f'{category_name},{application_domain}':
                    aaa.append(f'{my_dict[key]}')
        aaa = ','.join(aaa)
        print(f'"{category_name}",{aaa}')






if __name__ == '__main__':
    # get_top_10_security_policy_category_and_primary_language_distribution()
    get_application_domain_distribution()
    # get_application_domains_and_security_policy_category()
