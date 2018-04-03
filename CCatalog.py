from typing import Callable

import requests
import bs4
from bs4 import BeautifulSoup
from pprint import pprint


schedule_link = 'https://my.sa.ucsb.edu/public/curriculum/coursesearch.aspx'


def build_payload(page: requests.models.Response, subject: str, quarter: str, level: str) -> dict:
    soup = BeautifulSoup(page.content, 'html5lib')
    return {
        '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'],
        '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'],
        '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'],
        'ctl00$pageContent$courseList': subject,
        'ctl00$pageContent$dropDownCourseLevels': level,
        'ctl00$pageContent$quarterList': quarter,
        'ctl00$pageContent$searchButton.x': 0,
        'ctl00$pageContent$searchButton.y': 0,
    }


def schedule_parser(page: requests.models.Response) -> list:
    soup = BeautifulSoup(page.content, 'html5lib')
    course_table = soup.find('table', {'class': 'gridview'})
    course_rows = course_table.find_all('tr', {'class': 'CourseInfoRow'})
    courses = []
    for row in course_rows:
        # pre-process raw data
        cells = [cell for cell in row.find_all('td', recursive=False)]
        instructors = [node.strip()
                       for node
                       in row.find_all('td', recursive=False)[5].contents
                       if isinstance(node, bs4.element.NavigableString)]
        space = cells[9].text.strip().split()
        time = cells[7].text.strip().split()
        # collect data
        courses.append({
            'id': ' '.join(cells[1].contents[0].strip().split()),
            'title': cells[2].text.strip(),
            'enroll_code': cells[4].find('a').text.strip(),
            'instructors': list(filter(None, instructors)),
            'days': [d for d in cells[6].text.strip() if d.isalpha()],
            'time_start': time[0] if len(time) == 3 else ''.join(time[:2]),
            'time_end': time[2] if len(time) == 3 else ''.join(time[3:]),
            'location': ' '.join(cells[8].text.strip().split()),
            'enrolled': int(space[0]),
            'capacity': int(space[2]),
        })
    return courses


def schedule_search(subject: str, quarter: str, level: str,
                    parser: Callable[[requests.models.Response], list]=schedule_parser) -> list:
    s = requests.Session()
    schedule_init = s.get(schedule_link)
    options = schedule_search_options(schedule_init)
    if subject in options['subjects'] and quarter in options['quarters'] and level in options['levels']:
        schedule_page = s.post(schedule_link, data=build_payload(schedule_init, subject, quarter, level))
        return parser(schedule_page)
    return []


def schedule_search_options(page: requests.models.Response=None) -> dict:
    page = page or requests.get(schedule_link)
    soup = BeautifulSoup(page.content, 'html5lib')
    return {
        'subjects': [option['value'] for option in soup.find(id='ctl00_pageContent_courseList').find_all('option')],
        'quarters': [option['value'] for option in soup.find(id='ctl00_pageContent_quarterList').find_all('option')],
        'levels': [option['value'] for option in soup.find(id='ctl00_pageContent_dropDownCourseLevels').find_all('option')],
    }


if __name__ == '__main__':
    ...
    # options = schedule_search_options()
    # for item in options:
    #     print(f'{item}: {options[item]}')
    # for subject in options['subjects']:
    #     courses = schedule_search(subject, '20182', 'Undergraduate')
    #     for course in courses:
    #         print(course)

    # cs_20182_ugrad = schedule_search('CMPSC', '20182', 'Undergraduate')
    # for item in cs_20182_ugrad:
    #     print(item)

    # pprint([cs8 for cs8 in courses if cs8['id'] == 'CMPSC 8'])

    # schedule_search_available_choices()
