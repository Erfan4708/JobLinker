from __future__ import absolute_import, unicode_literals
from selenium import webdriver
from time import sleep
import os
import re
import time
from selenium.webdriver.common.by import By
from celery import shared_task
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
from .models import Post
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from django.db.models import F
from django.db.models import Q

SELENIUM_HUB_URL = f"http://{os.environ.get('SELENIUM_REMOTE_HOST', 'selenium-hub')}:4444/wd/hub"

JOBINJA_URL = "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1?preferred_before={preferred_before}&sort_by=published_at_desc&page={page}"
JOBVISION_URL = "https://jobvision.ir/jobs/category/developer?page={page}&sort=0"
E_ESTEKHDAM_URL = "https://www.e-estekhdam.com/search/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3--%D9%85%D9%87%D9%86%D8%AF%D8%B3-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D8%B7%D8%B1%D8%A7%D8%AD-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%D8%B4%D8%A8%DA%A9%D9%87--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D8%B4%D8%A8%DA%A9%D9%87--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%B4%D8%A8%DA%A9%D9%87-%D9%87%D8%A7%DB%8C-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C--Help-Desk--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AF%DB%8C%D8%AC%DB%8C%D8%AA%D8%A7%D9%84-%D9%85%D8%A7%D8%B1%DA%A9%D8%AA%DB%8C%D9%86%DA%AF--%D9%88%D8%B1%D8%AF%D9%BE%D8%B1%D8%B3-%DA%A9%D8%A7%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-SEO--%D8%AA%DA%A9%D9%86%D8%B3%DB%8C%D9%86-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D9%BE%D8%B4%D8%AA%DB%8C%D8%A8%D8%A7%D9%86-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%AF%D9%88%D8%B1%D8%A8%DB%8C%D9%86-%D9%88-%D8%AF%D8%B2%D8%AF%DA%AF%DB%8C%D8%B1--%D9%85%D8%AA%D8%AE%D8%B5%D8%B5-%D9%BE%D8%A7%DB%8C%DA%AF%D8%A7%D9%87-%D8%AF%D8%A7%D8%AF%D9%87--%D8%B7%D8%B1%D8%A7%D8%AD-UI|UX--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%A7%D9%85%D9%86%DB%8C%D8%AA-%D8%B3%D8%A7%DB%8C%D8%A8%D8%B1%DB%8C--%DA%A9%D8%A7%D8%B1%D8%B4%D9%86%D8%A7%D8%B3-%D8%AA%D8%B3%D8%AA-%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%BE%D8%B1%D9%88%DA%98%D9%87-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D8%B3%D8%B1%D9%88%D8%B1--%D9%85%D8%AF%DB%8C%D8%B1-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA--%D9%86%D8%B5%D8%A7%D8%A8-%D8%A7%DB%8C%D9%86%D8%AA%D8%B1%D9%86%D8%AA--%DA%AF%D8%B1%D8%A7%D9%81%DB%8C%D8%B3%D8%AA-%D9%88%D8%A8--%D8%AF%DA%A9%D9%84-%DA%A9%D8%A7%D8%B1--%D9%86%D8%B5%D8%A7%D8%A8-%D8%B4%D8%A8%DA%A9%D9%87?page={page}"

options = webdriver.FirefoxOptions()


def create_driver():
    return webdriver.Remote(
        command_executor=SELENIUM_HUB_URL,
        options=options,
    )


@shared_task
def jobinja_scrap():
    driver = create_driver()
    try:
        # Pin the listing to the moment the task started so pagination stays consistent
        preferred_before = int(time.time())
        page = 1
        driver.get(JOBINJA_URL.format(preferred_before=preferred_before, page=page))
        wait = WebDriverWait(driver, 10)
        while True:
            hrefs = driver.find_elements(By.XPATH, "//a[@class='c-jobListView__titleLink']")
            icons = driver.find_elements(By.XPATH,
                                         "//i[@class='c-jobListView__metaItemIcon c-icon c-icon--12x12 c-icon--place']")
            passed_days_elements = driver.find_elements(By.XPATH, "//span[@class='c-jobListView__passedDays']")
            if not hrefs:
                # An empty page means we went past the last page
                break

            for href, passed_days, icon in zip(hrefs, passed_days_elements, icons):
                try:
                    location = icon.find_element(By.XPATH, "./following-sibling::*[1]").text

                    # "(N روز پیش)" -> N days ago, "(امروز)" -> today, otherwise -1 (urgent ad)
                    numbers = re.findall(r'\d+', passed_days.text)
                    if numbers:
                        date_modified = int(numbers[0])
                    elif passed_days.text == "(امروز)":
                        date_modified = 0
                    else:
                        date_modified = -1

                    href.click()
                    all_handle = driver.window_handles
                    driver.switch_to.window(all_handle[-1])

                    title = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='c-jobView__titleText']//*"))).text
                    company_name = driver.find_element(By.XPATH, "//h2[@class='c-companyHeader__name']").text
                    detail = driver.find_element(By.XPATH,
                                                 "//section[@class='c-jobView o-box o-box--padded u-marginBottom40']").text
                    description = "-"
                    date_crawled = timezone.now()
                    link = driver.find_element(By.XPATH,
                                               "//a[@class='c-sharingJobOnMobile__uniqueURL u-textSmall c-muteLink']").text

                    link_exists = Post.objects.filter(Q(link=link) & ~Q(date_modified=-1)).exists()
                    if link_exists:
                        print(f"Link '{link}' already exists in the database. Skipping scraping.")
                    else:
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
                        save_to_postgres(dictionary, "jobinja")

                    driver.close()
                    sleep(0.5)
                    driver.switch_to.window(all_handle[0])
                    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='c-jobListView__titleLink']")))

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
            driver.get(JOBINJA_URL.format(preferred_before=preferred_before, page=page))
            sleep(4)
    finally:
        driver.quit()


@shared_task
def jobvision_scrap():
    driver = create_driver()
    try:
        page = 1
        driver.get(JOBVISION_URL.format(page=page))
        driver.set_window_size(800, 4000)
        sleep(2)
        href = driver.find_elements(By.XPATH, "//job-card[contains(@class,'col-12 row')]//a")[0]
        href.click()
        sleep(2)

        wait = WebDriverWait(driver, 10)
        title_element = ""
        while True:
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
                        label = driver.find_element(By.XPATH, '//*[text()="محل کار"]')
                        location = label.find_element(By.XPATH, './following-sibling::*[1]').text
                    except NoSuchElementException:
                        label = driver.find_element(By.XPATH, '//*[text()="Location"]')
                        location = label.find_element(By.XPATH, './following-sibling::*[1]').text
                    except:
                        location = "-"

                    try:
                        div_date_modified = driver.find_element(By.XPATH,
                                                                '//div[@class="col-12 row p-3"]//*[contains(text(), "روز پیش")]').text
                        date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                    except NoSuchElementException:
                        try:
                            div_date_modified = driver.find_element(By.XPATH,
                                                                    '//div[@class="col-12 row p-3"]//*[contains(text(), "days ago")]').text
                            date_modified = int(re.findall(r'\d+', div_date_modified)[0])
                        except NoSuchElementException:
                            date_modified = 0

                    date_crawled = timezone.now()
                    link = driver.current_url
                    link_exists = Post.objects.filter(Q(link=link) & ~Q(date_modified=-1)).exists()
                    if link_exists:
                        print(f"Link '{link}' already exists in the database. Skipping scraping.")
                    else:
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
                        next_button = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                        next_button.click()
                    except NoSuchElementException:
                        driver.get(JOBVISION_URL.format(page=page))
                        sleep(4)
                        driver.find_element(By.XPATH, f"//*[text()='{title_element}']").click()
                        try:
                            next_button = driver.find_element(By.XPATH,
                                                              "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                            next_button.click()
                        except NoSuchElementException:
                            page += 1
                            driver.get(JOBVISION_URL.format(page=page))
                            sleep(2)

                except:
                    driver.get(JOBVISION_URL.format(page=page))
                    sleep(4)
                    try:
                        driver.find_element(By.XPATH, f"//*[text()='{title_element}']").click()
                    except:
                        page += 1
                        driver.get(JOBVISION_URL.format(page=page))
                        sleep(2)
                        job_cards = driver.find_elements(By.XPATH, "//job-card[contains(@class,'col-12 row')]//a")
                        if not job_cards:
                            # No job cards on the next page, so every page has been visited
                            return
                        job_cards[0].click()
                        break
                    try:
                        next_button = driver.find_element(By.XPATH, "/html/body/app-root/div/job-detail/section/div[3]/a[2]")
                        next_button.click()
                    except NoSuchElementException:
                        page += 1
                        driver.get(JOBVISION_URL.format(page=page))
                        sleep(2)

            page += 1
    finally:
        driver.quit()


@shared_task
def e_estekhdam_scrap():
    driver = create_driver()
    try:
        page = 1
        driver.get(E_ESTEKHDAM_URL.format(page=page))
        wait = WebDriverWait(driver, 10)

        while True:
            job_items = driver.find_elements(By.XPATH, "//div[@class='job-list-item item hrm ']")
            if not job_items:
                # An empty page means we went past the last page
                break

            for job_item in job_items:
                job_item.click()
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

                # The province is shown in different ways depending on the ad
                location = ""
                for xpath in ("//div[text()='استان']/following-sibling::*[1]",
                              "//div[text()='Province']/following-sibling::*[1]",
                              '//strong[contains(text(), "استان")]',
                              '//strong[contains(text(), "province")]'):
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        location = elements[0].text
                        break

                try:
                    detail = driver.find_element(By.XPATH, "//div[@class='row ff-viewport']").text
                except NoSuchElementException:
                    detail = driver.find_element(By.XPATH, "//div[@class='entry-content ']").text
                description = ""
                date_crawled = timezone.now()
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
            driver.get(E_ESTEKHDAM_URL.format(page=page))
    finally:
        driver.quit()


def save_to_postgres(data, website):
    # Urgent ads are scraped again on every run, so update the existing
    # row for a link instead of inserting a duplicate
    Post.objects.update_or_create(
        link=data['link'],
        defaults={
            'title': data['title'],
            'company_name': data['company_name'],
            'date_modified': data['date_modified'],
            'description_position': data['description_position'],
            'detail_position': data['detail_position'],
            'location': data['location'],
            'website': website,
            'date_crawled': data['date_crawled'],
        },
    )


@shared_task
def update_database():
    # Runs daily: one more day has passed for every ad that isn't urgent
    Post.objects.exclude(date_modified=-1).update(date_modified=F('date_modified') + 1)
