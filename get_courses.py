from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pprint
import time
import json
import os


def get_timetable(dept, prog):

    dept_list = []

    # Setup Driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('log-level=3')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('no-sandbox')
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    # driver = webdriver.Firefox()
    driver.get('http://studentssp.wit.ie/Timetables/POSTT.aspx')

    whole_page = BeautifulSoup(driver.page_source, 'html.parser')
    select = whole_page.find('select', id='CboDept')
    for option in select.find_all('option'):
        if option['value'] != '  ':
            dept_list.append({'code': option['value'], 'name': option.text})

    print(dept_list)
    # time.sleep(200)
    # Fill Form
    # Department Select
    for dept in dept_list:
        Select(driver.find_element_by_id('CboDept')).select_by_value(dept['code'])
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        course_list = []

        select = soup.find('select', id='CboPOS')
        for option in select.find_all('option'):
            if option['value'] != '  ':
                course_list.append({'code': option['value'], 'name': option.text})

        dept['courses'] = course_list

    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(dept_list)

    with open('timetable.json', 'w') as outfile:
        json.dump(dept_list, outfile)


if __name__ == '__main__':
    get_timetable('SP', 'KINTT_B_Y4')
