import configparser
import os

from DBManager import DBManager, Course
from CCatalog import schedule_search_options, schedule_search


config = configparser.ConfigParser()
config.read('config')
DB_PATH = config.get('database', 'db_path')
DB_FILE = config.get('database', 'db_file')


if __name__ == '__main__':
    db = DBManager(os.path.join(DB_PATH, DB_FILE))
    options = schedule_search_options()

    quarter = '20181'
    level = 'Undergraduate'

    for item in options:
        print(f'{item}: {options[item]}')

    subject = 'CMPSC'
    print(f'{subject}:{quarter}:{level}')
    courses = schedule_search(subject, quarter, level)
    for course in courses:
        db.merge(Course.build(course, quarter, level))
