from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

import time

chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chrome_options)

driver.get("https://e.mail.ru/inbox/?back=1")


wait = WebDriverWait(driver, 3)
account_field = wait.until(EC.presence_of_element_located((By.NAME, 'username')))

account_field.send_keys('study.ai_172@mail.ru')
account_field.submit()

password_field = wait.until(EC.element_to_be_clickable((By.NAME, 'password')))

password_field.send_keys('NextPassword172!!!')
password_field.submit()

links_list = list()

while True:
    try:
        letters_link = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'llc')]")))
        actions = ActionChains(driver)

        for i in letters_link:
            links_list.append(i.get_attribute('href'))

        actions.move_to_element(letters_link[-1])
        actions.perform()
    except TimeoutException:
        break
print()
