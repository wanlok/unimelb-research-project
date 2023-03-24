import sys

import requests as requests

from utils import get_secret

# https://docs.gitlab.com/ee/api/dependencies.html
package_managers = [
    'bundler',
    'composer',
    'conan',
    'go',
    'gradle',
    'maven',
    'npm',
    'nuget',
    'pip',
    'pipenv',
    'yarn',
    'sbt',
    'setuptools'
]

content = '''
fragment content on Repository {
    dependencyGraphManifests {
        edges {
            node {
                blobPath
                dependencies {
                    nodes {
                        packageName
                        requirements
                        packageManager
                        repository {
                            url
                        }
                    }
                }
            }
        }
    }
}
'''

if __name__ == '__main__':
    slices = sys.argv[1].split('/')
    owner = slices[0]
    repo = slices[1]
    personal_access_token = get_secret()['personal_access_token']
    headers = {
        'Accept': 'application/vnd.github.hawkgirl-preview+json',
        'Authorization': f'token {personal_access_token}'
    }
    locations = ['organization', 'user']
    for location in locations:
        json = {'query': f'{content}query {{{location}(login: \"{owner}\") {{repository(name: \"{repo}\") {{...content}}}}}}'}
        json = requests.post('https://api.github.com/graphql', json=json, headers=headers).json()
        if 'errors' not in json:
            dependency_dict = dict()
            paths = set()
            files = map(lambda x: x['node'], json['data'][location]['repository']['dependencyGraphManifests']['edges'])
            for file in files:
                path = file['blobPath']
                paths.add(path)
                slices = path.split('/')
                lock_file = len(slices) > 0 and 'lock' in slices[len(slices) - 1].lower()
                if not lock_file:
                    dependencies = list(filter(lambda x: x['packageManager'].lower() in package_managers, file['dependencies']['nodes']))
                    if len(dependencies) > 0:
                        for dependency in dependencies:
                            name = dependency['packageName']
                            requirements = dependency['requirements']
                            package_manager = dependency['packageManager'].lower()
                            if dependency['repository'] is None:
                                repository = None
                            else:
                                repository = dependency['repository']['url']
                            if package_manager not in dependency_dict:
                                dependency_dict[package_manager] = set()
                            dependency_dict[package_manager].add((path, name, requirements, repository))
            for package_manager in dependency_dict:
                dependency_set = dependency_dict[package_manager]
                print(f'{package_manager} {len(dependency_set)}')
                for dependency in dependency_set:
                    path, name, requirements, repository = dependency
                    print(f'path: {path}, name: {name}, requirements: {requirements}, repository: {repository}')
            for path in paths:
                if '.github' not in path.lower():
                    print(path)
            break
