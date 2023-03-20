import sys

import nvdcve


rating_names = ['Low', 'Medium', 'High', 'Critical', 'None']


def get_v2_rating(score):
    rating = 'None'
    score = 0 if score is None or len(score) == 0 else float(score)
    if score >= 0.0 and score <= 3.9:
        rating = 'Low'
    elif score >= 4.0 and score <= 6.9:
        rating = 'Medium'
    elif score >= 7.0 and score <= 10.0:
        rating = 'High'
    return rating


def get_v3_rating(score):
    rating = 'None'
    score = 0 if score is None or len(score) == 0 else float(score)
    if score >= 0.1 and score <= 3.9:
        rating = 'Low'
    elif score >= 4.0 and score <= 6.9:
        rating = 'Medium'
    elif score >= 7.0 and score <= 8.9:
        rating = 'High'
    elif score >= 9.0 and score <= 10.0:
        rating = 'Critical'
    return rating


def increment_rating(list, name):
    i = rating_names.index(name)
    list[i] = list[i] + 1


def increment_number(list, num):
    if len(num) > 0:
        i = int(float(num))
        if i == len(list):
            i = i - 1
        list[i] = list[i] + 1


def rating(my_list):
    return ', '.join(list(map(lambda x: f'{rating_names[x[0]]}: {x[1]}', filter(lambda x: x[1] > 0, enumerate(my_list)))))


def number(my_list):
    return my_list


if __name__ == '__main__':
    repo = sys.argv[1]
    cve_list = nvdcve.get_list(repo)
    date_dict = dict()
    for cve in cve_list:
        date_dict[int(cve[1][:-2])] = 1
    date_list = list(date_dict.keys())
    date_list.sort()
    for date in date_list:
        cve_list = nvdcve.get_list(repo, f'{date}99')
        v2_i_rating_list = [0, 0, 0, 0, 0]
        v2_i_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v2_e_rating_list = [0, 0, 0, 0, 0]
        v2_e_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v3_i_rating_list = [0, 0, 0, 0, 0]
        v3_i_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        v3_e_rating_list = [0, 0, 0, 0, 0]
        v3_e_number_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for cve in cve_list:
            increment_rating(v2_i_rating_list, get_v2_rating(cve[2]))
            increment_number(v2_i_number_list, cve[2])
            increment_rating(v2_e_rating_list, get_v2_rating(cve[3]))
            increment_number(v2_e_number_list, cve[3])
            increment_rating(v3_i_rating_list, get_v3_rating(cve[4]))
            increment_number(v3_i_number_list, cve[4])
            increment_rating(v3_e_rating_list, get_v3_rating(cve[5]))
            increment_number(v3_e_number_list, cve[5])
        print(f'{date}')
        print(f'Version 2 Impact        : {number(v2_i_number_list)} {rating(v2_i_rating_list)}')
        print(f'Version 2 Explotability : {number(v2_e_number_list)} {rating(v2_e_rating_list)}')
        print(f'Version 3 Impact        : {number(v3_i_number_list)} {rating(v3_i_rating_list)}')
        print(f'Version 3 Explotability : {number(v3_e_number_list)} {rating(v3_e_rating_list)}')
