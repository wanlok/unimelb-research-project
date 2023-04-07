from chart import security_md_by_date_plot
from repository import get_security_advisories
from utils import get_start_and_end_date_string_before_date_minus_days

date_function = get_start_and_end_date_string_before_date_minus_days
y_function = get_security_advisories
y_title = 'Number of Security Advisories {} Days Before'
chart_directory_path = 'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\4\\'


if __name__ == '__main__':
    security_md_by_date_plot(date_function, y_function, y_title, chart_directory_path)