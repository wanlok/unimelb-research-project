from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import get_secret

if __name__ == '__main__':
    secret = get_secret()
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://github.com/login')
    driver.find_element(By.ID, 'login_field').send_keys(secret['username'])
    driver.find_element(By.ID, 'password').send_keys(secret['password'])
    driver.find_element(By.ID, 'password').parent.find_element(By.NAME, 'commit').click()
    page = 1
    while True:
        driver.get(f'https://github.com/search?l=Markdown&p={page}&q=SECURITY.md&type=Code')
        try:
            code_search_results = driver.find_element(By.ID, 'code_search_results')
            for div_1 in code_search_results.find_elements(By.TAG_NAME, 'div')[0].find_elements(By.TAG_NAME, 'div'):
                div_2 = div_1.find_elements(By.TAG_NAME, 'div')
                if len(div_2) > 0:
                    div_3 = div_2[0].find_elements(By.TAG_NAME, 'div')
                    if len(div_3) >= 2:
                        repo = div_3[0].find_elements(By.TAG_NAME, 'a')[0].get_attribute('innerHTML').strip()
                        url = div_3[1].find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
                        print(f'{repo} {url}')
            page = page + 1
        except NoSuchElementException:
            break
    driver.close()
