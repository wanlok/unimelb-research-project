import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import csv_reader, csv_writer, prepare_csv_file, get_secret

if __name__ == '__main__':
    repo_csv_file_path = '../repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    repo_csv_rows = prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    secret = get_secret()
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://github.com/login')
    driver.find_element(By.ID, 'login_field').send_keys(secret['username'])
    driver.find_element(By.ID, 'password').send_keys(secret['password'])
    driver.find_element(By.ID, 'password').parent.find_element(By.NAME, 'commit').click()
    page = 1
    while page <= 100:
        url_string = f'https://github.com/search?q=SECURITY.md&type=commits&p={page}'
        print(f'url: {url_string}')
        driver.get(url_string)
        repositories = driver.find_element(By.ID, 'commit_search_results').find_elements(By.CLASS_NAME, 'Link--secondary')
        for repository in repositories:
            row = [repository.get_attribute('innerHTML').strip()]
            if row not in repo_csv_rows:
                repo_csv_writer.writerow(row)
                repo_csv_rows.append(row)
        page = page + 1
        time.sleep(1)
    driver.close()
