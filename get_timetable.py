from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


def get_day(number):
    day_map = {
        1: "Monday",
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday'
    }

    return day_map[number]


def get_groups(groups_str):
    return groups_str.replace(' ', '').split('/')


def get_lecturer(lecturer):
    return ' '.join(lecturer.split(',')[::-1]).replace(' ', '', 1)


def get_timetable(dept, prog):

    # Setup Driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Firefox()
    driver.get('http://studentssp.wit.ie/Timetables/POSTT.aspx')

    # Fill Form
    # Department Select
    Select(driver.find_element_by_id('CboDept')).select_by_value(dept)
    # Programme Select
    Select(driver.find_element_by_id('CboPOS')).select_by_value(prog)
    # Week Select
    Select(driver.find_element_by_id('CboWeeks')).select_by_value("22")
    # Request Timetable
    driver.find_element_by_id('BtnRetrieve').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    timetable = soup.find(id='divTT').find_all('tr')
    day_idx = 0
    blank_timetable = []
    complete_timetable = []

    # Get each row that's a day name (Monday, Tuesday, etc.)
    for row in timetable:
        blank_timetable.append(row.findChildren('td', class_="darkbold"))

    # Fill each day in sequentially from the original list of rows
    for idx, item in enumerate(blank_timetable):
        if len(item) != 0:
            day_idx += 1
        else:
            if day_idx >= 1:
                curr_day = timetable[idx].findChildren('td')
                # Remove any blank entries
                if curr_day[1].get_text(strip=True) == '':
                    continue
                complete_timetable.append({"day": get_day(day_idx), "time": curr_day[0].get_text(strip=True), "name": curr_day[1].get_text(strip=True), "groups": get_groups(curr_day[2].get_text(strip=True)),
                                           "size": curr_day[3].get_text(strip=True), "type": curr_day[4].get_text(strip=True), "duration": curr_day[5].get_text(strip=True), "lecturer": get_lecturer(curr_day[6].get_text(strip=True)), "room": curr_day[7].get_text(strip=True)})

    group_timetable = []

    for idx, entry in enumerate(complete_timetable):
        # if 'kintt_b4W_W' in entry['groups'] or 'kintt_b4W_W2' in entry['groups']:
        entry['id'] = idx
        entry['ignore'] = False
        if 'online' in str(entry['type']).lower():
            entry['online'] = True
        else:
            entry['online'] = False
        entry['type'] = entry['type'].replace('OnLine', 'Online').replace('OnCampus', 'On Campus')
        group_timetable.append(entry)

    # for item in group_timetable:
    #     print(item)
    # unique_classes = list({v['lecturer']: v for v in group_timetable}.values())

    # for item in unique_classes:
    #     print(item['lecturer'])

    # print('---')

    # unique_classes = list({v['lecturer']: v for v in complete_timetable}.values())

    # for item in unique_classes:
    #     print(item['lecturer'])

    # print(len(group_timetable))

    for idx, item in enumerate(group_timetable):
        if idx > 0:
            if item['name'] == group_timetable[idx - 1]['name'] and item['time'] == group_timetable[idx - 1]['time'] and item['groups'] == group_timetable[idx - 1]['groups']:
                group_timetable.remove(item)

    # print(len(group_timetable))

    return(group_timetable)


if __name__ == '__main__':
    get_timetable('SP', 'KINTT_B_Y4')
