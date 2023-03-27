import sys

import repository

if __name__ == '__main__':
        paths, dependency_dict = repository.get_dependencies(sys.argv[1])
        for package_manager in dependency_dict:
            dependency_set = dependency_dict[package_manager]
            print(f'{package_manager} {len(dependency_set)}')
            if len(sys.argv) > 2 and sys.argv[2] == 'a':
                for dependency in dependency_set:
                    path, name, requirements, repository = dependency
                    print(f'path: {path}, name: {name}, requirements: {requirements}, repository: {repository}')
        for path in paths:
            if '.github' not in path.lower():
                print(path)
