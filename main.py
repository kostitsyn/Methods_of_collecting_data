from selenium import webdriver

driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver')

driver.get('https://gb.ru/login')
