import sys

import nvdcve
import repository
from repository import get_dependencies
from utils import get_writer


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


if __name__ == '__main__':
    # show_details = len(sys.argv) > 2 and sys.argv[2] == 'a'

    # for repo in repository.get_list(100):
    #     repos, dependency_dict = read()
    #     if repo not in repos:
    #         update(dependency_dict, repo)
    #         write(dependency_dict)

    repos, dependency_dict = read()
    for key in dependency_dict:
        print(f'{key},{len(dependency_dict[key])}')