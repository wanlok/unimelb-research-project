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
    personal_access_token = get_secret()['personal_access_token']
    headers = {
        'Accept': 'application/vnd.github.hawkgirl-preview+json',
        'Authorization': f'token {personal_access_token}'
    }
    locations = ['organization', 'user']
    for location in locations:
        json = {'query': f'{content}query {{{location}(login: \"{slices[0]}\") {{repository(name: \"{slices[1]}\") {{...content}}}}}}'}
        json = requests.post('https://api.github.com/graphql', json=json, headers=headers).json()
        if 'errors' not in json:
            dependency_dict = dict()
            files = map(lambda x: x['node'], json['data'][location]['repository']['dependencyGraphManifests']['edges'])
            for file in files:
                file_path = file['blobPath']
                print(file_path)
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
                        dependency_dict[package_manager].add((name, requirements, repository))
            for package_manager in dependency_dict:
                print(package_manager)
                dependency_set = dependency_dict[package_manager]
                for dependency in dependency_set:
                    name, requirements, repository = dependency
                    print(f'name: {name}, requirements: {requirements}, repository: {repository}')
            break
