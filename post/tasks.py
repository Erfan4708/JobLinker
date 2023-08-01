from __future__ import absolute_import, unicode_literals
from celery import shared_task
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
from config.celery import app
import os
from selenium.webdriver.common.by import By


# SELENIUM_GRID_HOST = os.environ.get('SELENIUM_GRID_HOST', 'localhost')

print("Test Execution Started")
options = webdriver.FirefoxOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument('--ignore-ssl-errors=yes')
# options.add_argument('--ignore-certificate-errors')

@shared_task
def my_task_2():
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    driver.get('https://de.wikipedia.org/wiki/Selenium')
    print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    title = driver.find_element(By.XPATH, "//span[@class='mw-page-title-main']").text
    print("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
    print(title)
    # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    # sleep(20)
    # driver.quit()

    # driver = webdriver.Remote(
    #     options=FirefoxOptions(),
    #     command_executor="http://%s:4444" % SELENIUM_GRID_HOST
    # )
    # firefox_options = FirefoxOptions()
    # firefox_options.add_argument('--headless')
    # driver = webdriver.Remote(command_executor='http://firefox:4444/wd/hub', options=firefox_options)

# @shared_task(name="run_selenium_task")
# def run_selenium_task():
#     print("hello")
#     firefox_options = Options()
#     firefox_options.add_argument("--headless")  # اجرای بدون نمایش مرورگر
#     driver = webdriver.Firefox(options=firefox_options)
#
#     try:
#         print("1111111111111111111111111111111111111111111111111111111111111111111111111111111")
#         driver.get("https://www.google.com")  # وب‌سایت مورد نظر خود را وارد کنید
#         time.sleep(20)
#
#     finally:
#         print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    driver.quit()
