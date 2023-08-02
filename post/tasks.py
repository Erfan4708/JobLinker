from __future__ import absolute_import, unicode_literals
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
from config.celery import app
import os
from selenium.webdriver.common.by import By
from celery import shared_task
from selenium.webdriver.support.ui import WebDriverWait
import re
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from persiantools import digits
from .models import Post
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException




# SELENIUM_GRID_HOST = os.environ.get('SELENIUM_GRID_HOST', 'localhost')

print("Test Execution Started")
options = webdriver.FirefoxOptions()

@shared_task
def jobinja_scrap():
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    driver.get("https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1?preferred_before=1690617703&sort_by=published_at_desc")
    wait = WebDriverWait(driver, 10)
    page = 1
    # first_title = getting_the_new_data()
    check = False
    latest_post = Post.objects.order_by('-date_crawled').last(website="jobinja")
    latest_title = latest_post.title if latest_post else None
    latest_link = latest_post.link if latest_post else None

    while check == False:
        divs = driver.find_elements(By.XPATH, "//div[@class='o-listView__itemWrap c-jobListView__itemWrap u-clearFix']")
        hrefs = driver.find_elements(By.XPATH, "//a[@class='c-jobListView__titleLink']")
        icons = driver.find_elements(By.XPATH,
                                     "//i[@class='c-jobListView__metaItemIcon c-icon c-icon--12x12 c-icon--place']")
        date_modifieds = driver.find_elements(By.XPATH, "//span[@class='c-jobListView__passedDays']")
        for href, date_modified, icon, div in zip(hrefs, date_modifieds, icons, divs):
            try:
                location = icon.find_element(By.XPATH, "./following-sibling::*[1]").text
                print(date_modified.text)
                try:
                    div.find_element(By.XPATH, "//*[contains(text(), 'روز پیش')]")
                    # -1 mean Fori
                    date_modified = int(re.findall(r'\d+', date_modified.text)[0])
                    print(date_modified)
                except NoSuchElementException:
                    if date_modified.text == "(امروز)":
                        date_modified = 0
                    else:
                        date_modified = -1

                print(date_modified)

                href.click()

                all_handle = driver.window_handles
                driver.switch_to.window(all_handle[-1])

                title = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='c-jobView__titleText']//*"))).text
                print(title)

                company_name = driver.find_element(By.XPATH, "//h2[@class='c-companyHeader__name']").text
                detail = driver.find_element(By.XPATH,
                                             "//section[@class='c-jobView o-box o-box--padded u-marginBottom40']").text
                description = "-"
                date_crawled = datetime.now()
                link = driver.find_element(By.XPATH,
                                           "//a[@class='c-sharingJobOnMobile__uniqueURL u-textSmall c-muteLink']").text
                if title == latest_title and link == latest_link:
                    print("Data base is update")
                    check = True
                    break

                if isinstance(date_modified, int):
                    dictionary = {
                        "title": title,
                        "company_name": company_name,
                        "detail_position": detail,
                        "description_position": description,
                        "location": location,
                        "date_modified": date_modified,
                        "date_crawled": date_crawled,
                        "link": link,
                    }
                else:
                    dictionary = {
                        "title": title,
                        "company_name": company_name,
                        "detail_position": detail,
                        "description_position": description,
                        "location": location,
                        "date_modified": digits.fa_to_en(date_modified),
                        "date_crawled": date_crawled,
                        "link": link,
                    }
                save_to_postgres(dictionary, "jobinja")
                driver.close()
                title = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='c-jobListView__titleLink']")))
                driver.switch_to.window(all_handle[0])
                driver.switch_to.window(all_handle[0])

            except NoSuchElementException:
                print("NoSuchElementException!!!")
                continue
            except ElementNotInteractableException:
                print("ElementNotInteractableException!!!")
                continue
            except TimeoutException:
                print("TimeoutException!!!")
                continue
            except:
                continue
                
        page += 1
        driver.get(
            f"https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1?preferred_before=1690617703&sort_by=published_at_desc&page={page}")
    driver.quit()


def jobvision_scrap():
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    driver.get("https://jobvision.ir/jobs/category/developer?sort=0&page=1")
    driver.set_window_size(800, 4000)
    sleep(2)
    href = driver.find_elements(By.XPATH, "//job-card[contains(@class,'col-12 row')]//a")[0]
    href.click()
    sleep(2)

    def get_current_datetime_str():
        now = datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S.%f") + "+00"
        return datetime_str

    link__ = ""
    wait = WebDriverWait(driver, 10)
    hrefs = driver.find_elements(By.XPATH,
                                 "//a[@class='col-12 row align-items-start rounded pt-3 px-0 mb-3 mb-md-2 position-relative bg-white mobile-job-card shadow-sm pb-3']")
    page = 1
    check = False
    latest_post = Post.objects.order_by('-date_crawled').last(website="jobvision")
    latest_title = latest_post.title if latest_post else None
    latest_link = latest_post.link if latest_post else None
    while check == False:
        for i in range(30):
            try:
                title_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/app-root/div/job-detail/section/div[4]/div/div[2]/h1'))).text
                company_name = driver.find_element(By.XPATH,
                                                   "/html/body/app-root/div/job-detail/section/div[4]/div/div[2]/div/div/a").text
                detail = driver.find_element(By.XPATH,
                                             "/html/body/app-root/div/job-detail/section/div[5]/app-header-job-detail/header/div/div[2]/div/div[1]").text
                description = driver.find_element(By.XPATH,
                                                  "/html/body/app-root/div/job-detail/section/div[6]/div/div").text

                try:
                    _ = driver.find_element(By.XPATH, '//*[text()="محل کار"]')
                    location = _.find_element(By.XPATH, './following-sibling::*[1]').text
                except NoSuchElementException:
                    _ = driver.find_element(By.XPATH, '//*[text()="Location"]')
                    location = _.find_element(By.XPATH, './following-sibling::*[1]').text
                except:
                    _ = ""
                    location = "-"

                print(title_element)
                try:
                    div_date_modified = driver.find_element(By.XPATH, '//*[contains(text(), "روز پیش")]').text
                    date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                except NoSuchElementException:
                    try:
                        div_date_modified = driver.find_element(By.XPATH, '//*[contains(text(), "days ago")]').text
                        date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                    except NoSuchElementException:
                        date_modified = 0

                print(date_modified)
                date_crawled = datetime.now()
                link = driver.current_url
                if title_element == latest_title and link == latest_link:
                    print("Data base is update")
                    check = True
                    break
                dictionary = {
                    "title": title_element,
                    "company_name": company_name,
                    "date_modified": date_modified,
                    "description_position": description,
                    "detail_position": detail,
                    "link": link,
                    "location": location,
                    "date_crawled": date_crawled,
                }
                save_to_postgres(dictionary, "job_vision")

                try:
                    next = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                    next.click()
                except NoSuchElementException:
                    driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                    sleep(4)
                    driver.find_element(By.XPATH, f"//*[text()='{title_element}']").click()
                    try:
                        next = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                        next.click()
                    except NoSuchElementException:
                        page += 1
                        driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                        sleep(2)

            except:
                driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                sleep(4)
                try:
                    driver.find_element(By.XPATH, f"//*[text()='{title_element}']").click()
                except:
                    page += 1
                    driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                    sleep(2)
                    href = driver.find_elements(By.XPATH, "//job-card[contains(@class,'col-12 row')]//a")[0]
                    href.click()
                    break
                try:
                    next = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                    next.click()
                except NoSuchElementException:
                    page += 1
                    driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                    sleep(2)

        page += 1

    driver.quit()


def save_to_postgres(data, website):
    post = Post(
        website=website,
        title=data['title'],
        company_name=data['company_name'],
        detail_position=data['detail_position'],
        description_position=data['description_position'],
        location=data['location'],
        date_modified=data['date_modified'],
        date_crawled=data['date_crawled'],
        link=data['link']
    )
    post.save()
