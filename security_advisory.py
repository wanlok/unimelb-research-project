


if __name__ == '__main__':
    def get_issue_count(repo, start_date=None, end_date=None):
    created = ''
    if start_date is not None and end_date is not None:
        start = datetime.strptime(start_date, '%Y%m%d').strftime(date_format)
        end = datetime.strptime(end_date, '%Y%m%d').strftime(date_format)
        created = f' created:{start}..{end}'
    query = 'query {search(query:"repo:{1} is:issue{2}",type:ISSUE){issueCount}}'
    query = query.replace('{1}', repo)
    query = query.replace('{2}', created)
    print(query)
    json = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers).json()
    count = 0
    if 'errors' not in json:
        count = int(json['data']['search']['issueCount'])
    else:
        print(json)
    return count

