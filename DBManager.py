from sqlalchemy import Column, Integer, String, Boolean, create_engine, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

from datetime import time


Base = declarative_base()


class Course(Base):
    __tablename__ = 'courses'

    cid = Column(Integer, primary_key=True)
    id = Column(String)
    title = Column(String)
    enroll_code = Column(String)
    instructors = Column(String)
    days = Column(String)
    time_start = Column(Time)
    time_end = Column(Time)
    location = Column(String)
    enrolled = Column(Integer)
    capacity = Column(Integer)
    quarter = Column(String)
    level = Column(String)

    @staticmethod
    def build(course_info, quarter, level):
        return Course(id=course_info['id'],
                      title=course_info['title'],
                      enroll_code=course_info['enroll_code'],
                      instructors=' '.join(course_info['instructors']),
                      days=' '.join(course_info['days']),
                      time_start=Course.__str_to_time_py(course_info['time_start']),
                      time_end=Course.__str_to_time_py(course_info['time_end']),
                      location=course_info['location'],
                      enrolled=course_info['enrolled'],
                      capacity=course_info['capacity'],
                      quarter=quarter,
                      level=level,)

    @staticmethod
    def __str_to_time_py(timestr: str) -> time:
        """
        Converts a time string to Python time object.
        :param timestr: Time string of the format 'HH:MM[am/pm]'
        :return: A Python object created from timestr. On exception, time(0, 0, 0) is returned
        """
        try:
            hour, minute = map(int, timestr[:-2].split(':'))
            if timestr[-2:] == 'pm':
                hour += 12
                if hour == 24:
                    hour = 0
        except:
            hour, minute = 0, 0
        return time(hour=hour, minute=minute, second=0)

    def __str__(self):
        return f'<Course {self.quarter}:{self.id}:{self.title}>'


class DBManager(object):

    def __init__(self, db_url, echo=False):
        self.engine = create_engine(f'sqlite:///{db_url}', echo=echo)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def add(self, item):
        self.session.add(item)
        self.session.commit()

    def add_all(self, items):
        self.session.add_all(items)
        self.session.commit()

    def merge(self, item):
        self.session.merge(item)
        self.session.commit()

    def rollback(self):
        self.session.rollback()
