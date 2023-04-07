from chart import security_md_plot
from repository import get_security_advisories
from utils import get_start_and_end_date_string

title = 'Number of Security Advisories / Number of SECURITY.md Commits in GitHub Repositories 2022'
y_title = 'Number of Security Advisories'
file_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\Security Advisories.png'


def y_function(repo, start_date, end_date):
    return len(get_security_advisories(repo, start_date, end_date))


if __name__ == '__main__':
    start_date = '20220101'
    _, end_date = get_start_and_end_date_string('20221201')
    security_md_plot(start_date, end_date, y_function, title, y_title, file_path)