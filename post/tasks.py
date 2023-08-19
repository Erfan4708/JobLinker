from __future__ import absolute_import, unicode_literals
from selenium import webdriver
from time import sleep
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
from django.db.models import Max
from django.db.models import Q

options = webdriver.FirefoxOptions()

@shared_task
def jobinja_scrap():
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    driver.get(
        "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1?preferred_before=1690617703&sort_by=published_at_desc")
    wait = WebDriverWait(driver, 10)
    page = 1
    check_for_update = 0
    check = False
    window_handles = []
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
                except:
                    if date_modified.text == "(امروز)":
                        date_modified = 0
                    else:
                        date_modified = -1

                print(date_modified)

                href.click()
                all_handle = driver.window_handles
                window_handles.append(all_handle[-1])
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

                link_exists = Post.objects.filter(Q(link=link) & ~Q(date_modified=-1)).exists()
                if link_exists:
                    print(f"Link '{link}' already exists in the database. Skipping scraping.")
                    driver.close()
                    sleep(0.5)
                    driver.switch_to.window(all_handle[0])
                    title = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//a[@class='c-jobListView__titleLink']")))
                    continue

                if isinstance(date_modified, int):
                    dictionary = {
                        "title": title,
                        "company_name": company_name,
                        "date_modified": date_modified,
                        "description_position": description,
                        "detail_position": detail,
                        "link": link,
                        "location": location,
                        "date_crawled": date_crawled,
                    }
                else:
                    dictionary = {
                        "title": title,
                        "company_name": company_name,
                        "date_modified": digits.fa_to_en(date_modified),
                        "description_position": description,
                        "detail_position": detail,
                        "link": link,
                        "location": location,
                        "date_crawled": date_crawled,
                    }
                save_to_postgres(dictionary, "jobinja")
                driver.close()
                sleep(0.5)
                driver.switch_to.window(all_handle[0])
                title = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='c-jobListView__titleLink']")))


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
        sleep(4)
    driver.quit()


@shared_task
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

    wait = WebDriverWait(driver, 10)
    hrefs = driver.find_elements(By.XPATH,
                                 "//a[@class='col-12 row align-items-start rounded pt-3 px-0 mb-3 mb-md-2 position-relative bg-white mobile-job-card shadow-sm pb-3']")
    page = 1
    check = False
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
                    div_date_modified = driver.find_element(By.XPATH,
                                                            '//div[@class="col-12 row p-3"]//*[contains(text(), "روز پیش")]').text
                    date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                except NoSuchElementException:
                    try:
                        div_date_modified = driver.find_element(By.XPATH,
                                                                '//div[@class="col-12 row p-3"]//*[contains(text(), "days ago")]').text
                        date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                        date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                    except NoSuchElementException:
                        date_modified = 0

                print(date_modified)
                date_crawled = datetime.now()
                link = driver.current_url
                link_exists = Post.objects.filter(Q(link=link) & ~Q(date_modified=-1)).exists()
                if link_exists:
                    print(f"Link '{link}' already exists in the database. Skipping scraping.")
                    try:
                        next = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                        next.click()
                    except NoSuchElementException:
                        driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                        sleep(4)
                        driver.find_element(By.XPATH, f"//*[text()='{title_element}']").click()
                        try:
                            next = driver.find_element(By.XPATH,
                                                       "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                            next.click()
                        except NoSuchElementException:
                            page += 1
                            driver.get(f"https://jobvision.ir/jobs/category/developer?page={page}&sort=0")
                            sleep(2)
                    continue
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


@shared_task
def e_estekhdam_scrap():
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    driver.get(
        "https://www.e-estekhdam.com/search/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3--%D9%85%D9%87%D9%86%D8%AF%D8%B3-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D8%B7%D8%B1%D8%A7%D8%AD-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%D8%B4%D8%A8%DA%A9%D9%87--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D8%B4%D8%A8%DA%A9%D9%87--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%B4%D8%A8%DA%A9%D9%87-%D9%87%D8%A7%DB%8C-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C--Help-Desk--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AF%DB%8C%D8%AC%DB%8C%D8%AA%D8%A7%D9%84-%D9%85%D8%A7%D8%B1%DA%A9%D8%AA%DB%8C%D9%86%DA%AF--%D9%88%D8%B1%D8%AF%D9%BE%D8%B1%D8%B3-%DA%A9%D8%A7%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-SEO--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%AF%D9%88%D8%B1%D8%A8%DB%8C%D9%86-%D9%88-%D8%AF%D8%B2%D8%AF%DA%AF%DB%8C%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D9%BE%D8%A7%DB%8C%DA%AF%D8%A7%D9%87-%D8%AF%D8%A7%D8%AF%D9%87--%D8%B7%D8%B1%D8%A7%D8%AD-UI|UX--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%A7%D9%85%D9%86%DB%8C%D8%AA-%D8%B3%D8%A7%DB%8C%D8%A8%D8%B1%DB%8C--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AA%D8%B3%D8%AA-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%BE%D8%B1%D9%88%DA%98%D9%87-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D8%B3%D8%B1%D9%88%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%A7%DB%8C%D9%86%D8%AA%D8%B1%D9%86%D8%AA--%DA%AF%D8%B1%D8%A7%D9%81%DB%8C%D8%B3%D8%AA-%D9%88%D8%A8--%D8%AF%DA%A9%D9%84-%DA%A9%D8%A7%D8%B1--%D9%86%D8%B5%D8%A7%D8%A8-%D8%B4%D8%A8%DA%A9%D9%87?page=1")
    wait = WebDriverWait(driver, 10)

    page = 1
    check = True
    while check == True:
        hrefs = driver.find_elements(By.XPATH, "//div[@class='job-list-item item hrm ']")
        for href in hrefs:
            href.click()
            all_handle = driver.window_handles
            driver.switch_to.window(all_handle[-1])

            try:
                company_name = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'استخدام')]"))).text
            except NoSuchElementException:
                company_name = "استخدام در یک شرکت معتبر"
            except TimeoutException:
                try:
                    company_name = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'استخدام')]"))).text
                except NoSuchElementException:
                    company_name = "استخدام در یک شرکت معتبر"
                except TimeoutException:
                    sleep(5)
                    driver.close()
                    driver.switch_to.window(all_handle[0])
                    continue

            try:
                title = driver.find_element(By.XPATH, "//h1[@class='entry-title']").text
            except:
                title = "استخدام در یک شرکت معتبر"

            try:
                try:
                    _ = driver.find_element(By.XPATH, "//div[text()='استان']")
                    location = _.find_element(By.XPATH, './following-sibling::*[1]').text
                except NoSuchElementException:
                    _ = driver.find_element(By.XPATH, "//div[text()='Province']")
                    location = _.find_element(By.XPATH, './following-sibling::*[1]').text

            except NoSuchElementException:
                try:
                    location = driver.find_element(By.XPATH, '//strong[contains(text(), "استان")]').text
                except NoSuchElementException:
                    location = driver.find_element(By.XPATH, '//strong[contains(text(), "province")]').text
            except:
                try:
                    location = driver.find_element(By.XPATH, '//*[contains(text(), "استان")]').text
                except NoSuchElementException:
                    location = driver.find_element(By.XPATH, '//*[contains(text(), "province")]').text
                except:
                    location = ""

            try:
                detail = driver.find_element(By.XPATH, "//div[@class='row ff-viewport']").text
            except NoSuchElementException:
                detail = driver.find_element(By.XPATH, "//div[@class='entry-content ']").text
            description = ""
            date_crawled = datetime.now()
            link = driver.current_url
            link_exists = Post.objects.filter(Q(link=link) & ~Q(date_modified=-1)).exists()
            if link_exists:
                driver.close()
                driver.switch_to.window(all_handle[0])
                continue

            dictionary = {
                "title": title,
                "company_name": company_name,
                "detail_position": detail,
                "description_position": description,
                "location": location,
                "date_modified": 2,
                "date_crawled": date_crawled,
                "link": link,
            }
            save_to_postgres(dictionary, "e-estekhdam")
            driver.close()
            driver.switch_to.window(all_handle[0])

        page += 1
        driver.get(
            f"https://www.e-estekhdam.com/search/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3--%D9%85%D9%87%D9%86%D8%AF%D8%B3-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D8%B7%D8%B1%D8%A7%D8%AD-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%D8%B4%D8%A8%DA%A9%D9%87--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D8%B4%D8%A8%DA%A9%D9%87--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%B4%D8%A8%DA%A9%D9%87-%D9%87%D8%A7%DB%8C-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C--Help-Desk--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AF%DB%8C%D8%AC%DB%8C%D8%AA%D8%A7%D9%84-%D9%85%D8%A7%D8%B1%DA%A9%D8%AA%DB%8C%D9%86%DA%AF--%D9%88%D8%B1%D8%AF%D9%BE%D8%B1%D8%B3-%DA%A9%D8%A7%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-SEO--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%AF%D9%88%D8%B1%D8%A8%DB%8C%D9%86-%D9%88-%D8%AF%D8%B2%D8%AF%DA%AF%DB%8C%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D9%BE%D8%A7%DB%8C%DA%AF%D8%A7%D9%87-%D8%AF%D8%A7%D8%AF%D9%87--%D8%B7%D8%B1%D8%A7%D8%AD-UI|UX--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%A7%D9%85%D9%86%DB%8C%D8%AA-%D8%B3%D8%A7%DB%8C%D8%A8%D8%B1%DB%8C--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AA%D8%B3%D8%AA-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%BE%D8%B1%D9%88%DA%98%D9%87-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D8%B3%D8%B1%D9%88%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%A7%DB%8C%D9%86%D8%AA%D8%B1%D9%86%D8%AA--%DA%AF%D8%B1%D8%A7%D9%81%DB%8C%D8%B3%D8%AA-%D9%88%D8%A8--%D8%AF%DA%A9%D9%84-%DA%A9%D8%A7%D8%B1--%D9%86%D8%B5%D8%A7%D8%A8-%D8%B4%D8%A8%DA%A9%D9%87?page={page}")

    driver.quit()
def save_to_postgres(data, website):
    max_id = Post.objects.aggregate(Max('id'))['id__max']
    new_id = max_id + 1 if max_id is not None else 1

    post = Post(
        id=new_id,
        title=data['title'],
        company_name=data['company_name'],
        date_modified=data['date_modified'],
        description_position=data['description_position'],
        detail_position=data['detail_position'],
        link=data['link'],
        location=data['location'],
        website=website,
        date_crawled=data['date_crawled'],
    )

    print('save_to_postgres@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    post.save()


@shared_task
def update_database():
    posts_to_update = Post.objects.exclude(date_modified=-1)
    for post in posts_to_update:
        post.date_modified += 1
        post.save()
    print("date_modified += 1 . Done")
