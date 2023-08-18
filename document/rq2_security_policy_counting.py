from Levenshtein import distance

from document.hierarchical_agglomerative_clustering import get_users, get_names, get_contents, write_csv, \
    get_contents_by_security_policy_repos, dum_dum, as5, directory_path


def get_content_match_lists(user, directory, target_content, contents):
    match_list = []
    mismatch_list = []
    for content in contents:
        d = distance(target_content[1], content[1])
        # t = [user, directory, d, f'{directory_path}{target_content[0]}', f'{directory_path}{content[0]}']
        t = [user, directory, d, f'"{target_content[1]}"', f'"{content[1]}"']
        if d == 0:
            match_list.append(t)
        else:
            mismatch_list.append(t)
    return match_list, mismatch_list


def rq2_2_1():
    count_4 = 0
    count_5 = 0
    for user in users:
        names = get_names(user=user)
        contents = get_contents(names, show_path=show)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        parent_github_content_count = len(parent_github_contents)
        root_content_count = len(root_contents)
        github_content_count = len(github_contents)
        docs_content_count = len(docs_contents)
        if parent_github_content_count > 0:
            if root_content_count == 0 and github_content_count == 0 and docs_content_count == 0:
                count_4 = count_4 + 1
            else:
                count_5 = count_5 + 1
    print(f'{count_4} {count_5}')


def rq2_2_2():
    a_count = 0
    b_count = 0
    c_count = 0

    all_a_mismatch_list = []
    all_b_mismatch_list = []
    all_c_mismatch_list = []

    a_user_set = set()
    b_user_set = set()
    c_user_set = set()

    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        if len(parent_github_contents) > 0:
            parent_github_content = parent_github_contents[0]
            a_match_list, a_mismatch_list = get_content_match_lists(user, 'root', parent_github_content, root_contents)
            b_match_list, b_mismatch_list = get_content_match_lists(user, '.github', parent_github_content, github_contents)
            c_match_list, c_mismatch_list = get_content_match_lists(user, 'docs', parent_github_content, docs_contents)

            # if a_match_count > 0 or a_mismatch_count > 0:
            #     user_set.add(user)
            #     a_count = a_count + a_match_count + a_mismatch_count
            # if b_match_count > 0 or b_mismatch_count > 0:
            #     user_set.add(user)
            #     b_count = b_count + b_match_count + b_mismatch_count
            # if c_match_count > 0 or c_mismatch_count > 0:
            #     user_set.add(user)
            #     c_count = c_count + c_match_count + c_mismatch_count

            if len(a_mismatch_list) > 0:
                a_user_set.add(user)

            if len(b_mismatch_list) > 0:
                b_user_set.add(user)

            if len(c_mismatch_list) > 0:
                c_user_set.add(user)

            all_a_mismatch_list.extend(a_mismatch_list)
            all_b_mismatch_list.extend(b_mismatch_list)
            all_c_mismatch_list.extend(c_mismatch_list)

    for c in all_a_mismatch_list:
        print(c)
    print()
    print(a_user_set)
    print(len(a_user_set))
    print()
    for c in all_b_mismatch_list:
        print(c)
    print()
    print(b_user_set)
    print(len(b_user_set))
    print()
    for c in all_c_mismatch_list:
        print(c)
    print()
    print(c_user_set)
    print(len(c_user_set))
    print()

    # print(f'{len(user_set)} {a_count} {b_count} {c_count}')


def rq2_2_2_grouping():
    mismatch_list = []
    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        if len(parent_github_contents) > 0:
            parent_github_content = parent_github_contents[0]
            _, a_mismatch_list = get_content_match_lists(user, 'root', parent_github_content, root_contents)
            _, b_mismatch_list = get_content_match_lists(user, 'github', parent_github_content, github_contents)
            _, c_mismatch_list = get_content_match_lists(user, 'docs', parent_github_content, docs_contents)
            mismatch_list.extend(a_mismatch_list)
            mismatch_list.extend(b_mismatch_list)
            mismatch_list.extend(c_mismatch_list)
    my_dict = dict()
    for item in mismatch_list:
        key = f'{item[0]}{item[1]}{item[2]}'
        if key in my_dict:
            my_dict[key].append(item)
        else:
            my_dict[key] = [item]
    qqq = []
    for key in my_dict:
        # if len(my_dict[key]) > 1:
        d = my_dict[key][0][2]
        user = my_dict[key][0][0]
        a = my_dict[key][0][3]
        b = my_dict[key][0][4]
        lll = list(map(lambda x: f'{x}' if type(x) == int else f'"{x}"', my_dict[key][0]))
        lll = ','.join(lll)
        qqq.append((d, lll, a, b, user))
    qqq.sort(key=lambda x: x[0])
    for l in qqq:
        print(f'{l[4]},{l[0]},{len(l[2])},{len(l[3])},{"more" if len(l[2]) > len(l[3]) else "less"}')
        # print(f'{l[1][0]}{"more" if len(l[1][3]) > len(l[1][4]) else "less"}')

        # lll = []
        # for l in my_dict[key]:
        #     lll.append(l[4])
        # if len(lll) > 1:
        #     lll = ','.join(lll)
        #     print(lll)
        #
        #     #mmm = []
        #     #for i in range(len(lll)):
        #     #    mmm.append(distance(lll[0], lll[i]))
        #     #print(mmm)
        # print('//////////')


def get_security_policy(user, parent_github_contents, root_contents, github_contents, docs_contents):
    info = None
    number_of_parent_github_contents = len(parent_github_contents)
    if number_of_parent_github_contents > 0:
        parent_github_content = parent_github_contents[0]



        # a = dict()
        # b = dict()
        # c = dict()
        # for root_content in root_contents:
        #     max_change_length = max(len(parent_github_content[1]), len(root_content[1]))
        #     if max_change_length > 0:
        #         key = get_key_2(distance(parent_github_content[1], root_content[1]) / max_change_length)
        #         if key in a:
        #             a[key].append((parent_github_content[0], root_content[0]))
        #         else:
        #             a[key] = [(parent_github_content[0], root_content[0])]
        # for github_content in github_contents:
        #     max_change_length = max(len(parent_github_content[1]), len(github_content[1]))
        #     if max_change_length > 0:
        #         key = get_key_2(distance(parent_github_content[1], github_content[1]) / max_change_length)
        #         if key in b:
        #             b[key].append((parent_github_content[0], github_content[0]) )
        #         else:
        #             b[key] = [(parent_github_content[0], github_content[0])]
        # for docs_content in docs_contents:
        #     max_change_length = max(len(parent_github_content[1]), len(docs_content[1]))
        #     if max_change_length > 0:
        #         key = get_key_2(distance(parent_github_content[1], docs_content[1]) / max_change_length)
        #         if key in c:
        #             c[key].append((parent_github_content[0], docs_content[0]))
        #         else:
        #             c[key] = [(parent_github_content[0], docs_content[0])]

        info = (
            number_of_parent_github_contents,
            dum_dum(as5(parent_github_content, root_contents)),
            dum_dum(as5(parent_github_content, github_contents)),
            dum_dum(as5(parent_github_content, docs_contents))
        )
    return info
        # print(
        #     f'\"{user}\",{len(contents)},{number_of_parent_github_contents},{root_count},{root_same_count},{root_similar_count},{root_other_count},{github_count},{github_same_count},{github_similar_count},{github_other_count},{docs_count},{docs_same_count},{docs_similar_count},{docs_other_count}')


def rq2_2_3():
    a_count = 0
    b_count = 0
    b_match_count = 0
    c_count = 0
    c_match_count = 0
    d_count = 0
    d_match_count = 0
    user_set = set()
    for user in users:
        names = get_names(user=user)
        contents = get_contents(names, show_path=show)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)

        info = get_security_policy(user, parent_github_contents, root_contents, github_contents, docs_contents)


        if info is not None:
            parent_count, b, c, d = info
            if parent_count > 0:
                if b != (0, 0, 0, 0):
                    user_set.add(user)
                    count, match_count, _, _ = b
                    # print(b)

                    if match_count > 0:
                        print(f'b {user} {match_count}')

                    b_count = b_count + count
                    b_match_count = b_match_count + match_count
                if c != (0, 0, 0, 0):
                    user_set.add(user)
                    count, match_count, _, _ = c

                    if match_count > 0:
                        print(f'c {user} {match_count}')

                    # print(f'c {c} {user}')
                    c_count = c_count + count
                    c_match_count = c_match_count + match_count
                if d != (0, 0, 0, 0):
                    user_set.add(user)
                    count, match_count, _, _ = d

                    if match_count > 0:
                        print(f'd {user} {match_count}')

                    d_count = d_count + count
                    d_match_count = d_match_count + match_count
            a_count = a_count + 1
    print(f'HELLO WORLD {a_count} {b_count} {b_match_count} {c_count} {c_match_count} {d_count} {d_match_count}')
    print(f'USER {len(user_set)}')

if __name__ == '__main__':
    # rq2_2_1()
    # rq2_2_2()
    rq2_2_2_grouping()
    # rq2_2_3()

    # for user in users:
    #     names = get_names(user=user)
    #     contents = get_contents(names, show_path=show)
    #     write_csv(names, contents)
    #     parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
    #
    #     info = get_security_policy(parent_github_contents, root_contents, github_contents, docs_contents)
    #
    #     if info is not None:
    #         parent_count, b, c, d = info
    #         if parent_count > 0:
    #             if b != (0, 0, 0, 0):
    #                 count, match_count, _, _ = b
    #                 # print(b)
    #                 b_count = b_count + count
    #                 b_match_count = b_match_count + match_count
    #             if c != (0, 0, 0, 0):
    #                 count, match_count, _, _ = c
    #                 # print(f'c {c} {user}')
    #                 c_count = c_count + count
    #                 c_match_count = c_match_count + match_count
    #             if d != (0, 0, 0, 0):
    #                 count, match_count, _, _ = d
    #                 d_count = d_count + count
    #                 d_match_count = d_match_count + match_count
    #         a_count = a_count + 1

        # global_contents = []
        # if len(parent_github_contents) > 0:
        #     global_contents = global_contents + [parent_github_contents[0]]
        # if len(github_contents) > 0:
        #     global_contents = global_contents + github_contents
        # if len(docs_contents) > 0:
        #     global_contents = global_contents + docs_contents
        # if len(root_contents) > 0:
        #     global_contents = global_contents + root_contents


        # for row in root_distance_dict:
        #     print(root_distance_dict[row])

        # print(parent_github_distance_dict)
        # print(github_distance_dict)
        # print(docs_distance_dict)
        # print(root_distance_dict)


        # print(len(parent_github_contents))
        # print(len(github_contents))
        # print(len(docs_contents))
        # print(len(root_contents))

        # print(user)

        # if len(github_contents) > 0:
        #     i = i + len(github_contents)
        # if len(docs_contents) > 0:
        #     j = j + len(docs_contents)
        # if len(root_contents) > 0:
        #     k = k + len(root_contents)

        # get_statistics(user, 'AAAA', global_contents)
        # get_statistics(user, 'root', root_contents)
        # get_statistics(user, 'github', github_contents)
        # get_statistics(user, 'docs', docs_contents)