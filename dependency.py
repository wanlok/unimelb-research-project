import sys

import nvdcve
import repository
from repository import get_dependencies
from utils import get_writer, repos, csv_reader, sort_by_descending_values, dependency_file_path


def dummy(repo, show_details):
    paths, dependency_dict = get_dependencies(sys.argv[1])
    for package_manager in dependency_dict:
        dependency_set = dependency_dict[package_manager]
        print(f'{package_manager} {len(dependency_set)}')
        if show_details:
            for dependency in dependency_set:
                path, name, requirements, repository = dependency
                print(f'path: {path}, name: {name}, requirements: {requirements}, repository: {repository}')
    for path in paths:
        if '.github' not in path.lower():
            print(path)


def update(dependency_dict, repo):
    print(repo)
    _, package_manager_dict = get_dependencies(repo)
    dependency_set = set()
    for package_manager in package_manager_dict:
        for dependency in package_manager_dict[package_manager]:
            _, _, _, url = dependency
            if url is not None:
                slices = url.split('/')
                length = len(slices)
                if length >= 2:
                    dependency_repo = f'{slices[length - 2]}/{slices[length - 1]}'
                    if nvdcve.is_exists(dependency_repo):
                        dependency_set.add(dependency_repo)
    for key in dependency_set:
        if key in dependency_dict:
            dependency_dict[key].append(repo)
        else:
            dependency_dict[key] = [repo]


def write(dependency_dict):
    writer = get_writer(f'dependencies.txt')
    for key in sorted(dependency_dict.items(), key=lambda x: len(x[1]), reverse=True):
        writer.write(f'{key[0]} {key[1]}\n')


def read():
    repo_set = set()
    dependency_dict = dict()
    with open('dependencies.txt') as f:
        lines = f.readlines()
        for line in lines:
            slices = line.strip().split(' ', 1)
            dependency_name = slices[0]
            repos = eval(slices[1])
            dependency_dict[dependency_name] = repos
            repo_set.update(repos)
    return list(repo_set), dependency_dict


def get_package_manager_dict():
    package_manager_dict = None
    i = 0
    for row in csv_reader(dependency_file_path):
        if len(row[1]) > 0:
            if package_manager_dict is None:
                package_manager_dict = dict()
            repo = row[0]
            name_dict = eval(row[1])
            for package_manager in name_dict:
                t = (repo, list(name_dict[package_manager]))
                if package_manager in package_manager_dict:
                    package_manager_dict[package_manager].append(t)
                else:
                    package_manager_dict[package_manager] = [t]
            i = i + 1
    if package_manager_dict is not None and 'ACTIONS' in package_manager_dict:
        del package_manager_dict['ACTIONS']
    return package_manager_dict


# def get_github_url(package_manager, package_name):
#     print(f'{package_manager},{package_name}')
#     if package_manager == 'PIP':



def dummy_dummy(package_manager, b):
    distribution_dict = dict()
    values = []
    for repo, a_list in b:
        for name in a_list:
            if name in distribution_dict:
                distribution_dict[name] = distribution_dict[name] + 1
            else:
                distribution_dict[name] = 1
        values.extend(a_list)
    # print(get_values(values)[:100])
    # print(f'{package_manager} {len(get_values(values, percentage=1))} {len(distribution_dict.keys())}')
    i = 0
    for key in sort_by_descending_values(distribution_dict):
        value = distribution_dict[key]
        i = i + 1
        # get_github_url(package_manager, key)
        if 'log4j' in key:
            print(f'"{package_manager}","{key}",{value}')
        # if i == 30:
        #     break


def sort_list_as_count(my_dict):
    sorted_dict = dict()
    for key in my_dict:
        sorted_dict[key] = len(my_dict[key])
    sorted_dict = sort_by_descending_values(sorted_dict)
    return list(sorted_dict.keys())


def get_owner_distribution():
    package_manager_dict = get_package_manager_dict()
    for package_manager in package_manager_dict:
        owner_dict = dict()
        for _, dependency_urls in package_manager_dict[package_manager]:
            for dependency_url in dependency_urls:
                dependency_url = dependency_url.replace('https://github.com/', '')
                slices = dependency_url.split('/')
                owner = slices[0]
                project = slices[1]
                if owner in owner_dict:
                    if project in owner_dict[owner]:
                        owner_dict[owner][project] = owner_dict[owner][project] + 1
                    else:
                        owner_dict[owner][project] = 1
                else:
                    owner_dict[owner] = dict()
                    owner_dict[owner][project] = 1
        print()
        print(f'{package_manager} - - - - - - - - - -')
        for owner in sort_list_as_count(owner_dict)[:100]:
            project_dict = sort_by_descending_values(owner_dict[owner])
            number_of_project = len(project_dict)
            project_dict = [f'{key} {project_dict[key]}' for key in list(project_dict.keys())]
            print(f'{owner} {number_of_project} {project_dict}')
            # print(f'{owner} {number_of_project}')


def get_owner():
    owner_dict = dict()
    package_manager_dict = get_package_manager_dict()
    for package_manager in package_manager_dict:
        for _, dependency_repos in package_manager_dict[package_manager]:
            owner_set = set()
            for dependency_url in dependency_repos:
                dependency_url = dependency_url.replace('https://github.com/', '')
                slices = dependency_url.split('/')
                owner = slices[0]
                # project = slices[1]
                owner_set.add(owner)
            for owner in owner_set:
                owner = f'{package_manager}:{owner}'
                if owner in owner_dict:
                    owner_dict[owner] = owner_dict[owner] + 1
                else:
                    owner_dict[owner] = 1
    for owner in sort_by_descending_values(owner_dict):
        print(f'{owner} {owner_dict[owner]}')


def get_repo_x():
    package_manager_dict = get_package_manager_dict()
    repo_package_manager_dict = dict()
    for package_manager in package_manager_dict:
        total = 0
        repo_dependency_urls = package_manager_dict[package_manager]
        for repo, dependency_urls in repo_dependency_urls:
            total = total + len(dependency_urls)
            if repo in repo_package_manager_dict:
                repo_package_manager_dict[repo].add(package_manager)
            else:
                repo_package_manager_dict[repo] = {package_manager}
        print(f'{package_manager},{int(total / len(repo_dependency_urls))}')
    total = 0
    for repo in repo_package_manager_dict:
        total = total + len(repo_package_manager_dict[repo])
    # print(total / 2882)
    print(len(repo_package_manager_dict))


def get_repo_xx(repo, package_manager_dict):
    dependency_set = set()
    for package_manager in package_manager_dict:
        for r, l in package_manager_dict[package_manager]:
            if repo == r:
                dependency_set.update(l)
    value = f'{len(dependency_set)}'
    invalid_repos = ['iofinnet/tss-lib', 'iofinnet,root,0']
    return None if repo in invalid_repos else value


if __name__ == '__main__':
    # show_details = len(sys.argv) > 2 and sys.argv[2] == 'a'

    # for repo in repository.get_list(100):
    #     repos, dependency_dict = read()
    #     if repo not in repos:
    #         update(dependency_dict, repo)
    #         write(dependency_dict)

    # repos, dependency_dict = read()
    # for key in dependency_dict:
    #     print(f'{key},{len(dependency_dict[key])}')

    # get_owner_distribution()
    # get_owner()
    # get_repo_x()

    print(repos(get_repo_xx, get_package_manager_dict()))
    # get_repo_xx('VictoriaMetrics/VictoriaMetrics', get_package_manager_dict())