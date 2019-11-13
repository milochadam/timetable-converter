import copy
import re
from typing import List, Optional

from bs4 import BeautifulSoup, NavigableString
from course import Course
from settings import (DAY_NAMES_PRESENT, DAYS_COUNT, HOURS,
                      MERGE_CONSECUTIVE_COURSES, WEEKDAY_NAMES)


class HTMLParser:
    def __init__(self, soup, moves: Optional[list] = None) -> None:
        self.soup = soup
        self.moves = moves or []

    def parse(self) -> BeautifulSoup:
        new_plan = [[[] for y in range(HOURS)] for x in range(DAYS_COUNT)]
        s = self.soup
        table_body = s.find(name='tbody')

        # skip header
        for y, row in enumerate(table_body.find_all(name='tr')[1:]):
            # skip first cell with hour
            for x, cell in enumerate(row.find_all(name='td')[1:]):
                try:
                    courses = self._string_to_courses(cell.children)
                except Exception as e:
                    print(e, cell)
                new_plan[x][y].extend(courses)

        for (move_from, move_to) in self.moves:
            mfr = move_from.get('room')
            mfx = move_from.get('day') - 1
            mfy = move_from.get('hour') - 7

            mtx = move_to.get('day') - 1
            mty = move_to.get('hour') - 7

            matching_course = None
            for i in range(3):
                target_courses = new_plan[mfx][mfy + i]
                for j, course in enumerate(target_courses):
                    if course.room == mfr and (
                        matching_course is None or course == matching_course
                    ):
                        matching_course = course
                        new_plan[mtx][mty + i].append(course)
                        del new_plan[mfx][mfy + i][j]
                        break

        if MERGE_CONSECUTIVE_COURSES:
            for day in new_plan:
                for y, hour in enumerate(day):
                    if hour is []:
                        continue
                    for course in hour:
                        if course.checked:
                            course.delete = True
                            continue
                        next_hours = day[y + 1:]
                        for next_hour in next_hours:
                            matching_course = [
                                c for c in next_hour if course == c
                            ]
                            if len(matching_course) == 1:
                                matching_course[0].checked = True
                                course.hours += 1
                            else:
                                break

        new_soup = BeautifulSoup('<html></html>', 'html.parser')
        new_soup.insert(0, s.new_tag('body'))
        new_soup.insert(0, s.new_tag('head'))
        new_soup.head.insert(0, s.new_tag('meta', attrs={'charset': 'utf-8'}))

        timetable_div = s.new_tag('div')
        timetable_div['class'] = timetable_div.get('class', []) + [
            'timetable-container'
        ]
        new_soup.body.insert(0, timetable_div)
        hours_div = s.new_tag('div')
        for i in range(HOURS):
            hour_div = s.new_tag('div')
            hour_div['class'] = hour_div.get('class', []) + ['cell', 'hour']
            hour_div.string = f'{i + 7}:00'
            hours_div.append(hour_div)
        if DAY_NAMES_PRESENT:
            empty_cell = s.new_tag('div')
            empty_cell['class'] = empty_cell.get('class', []) + [
                'cell', 'empty-in-corner'
            ]
            hours_div.insert(0, empty_cell)
        timetable_div.insert(0, hours_div)
        for day_number, day in enumerate(new_plan):
            day_div = s.new_tag('div')
            day_div['class'] = day_div.get('class', []) + ['day']
            if DAY_NAMES_PRESENT:
                day_name_div = s.new_tag('div')
                day_name_div.string = WEEKDAY_NAMES[day_number]
                day_name_div['class'] = day_name_div.get('class',
                                                         []) + ['day-name']
                day_div.append(day_name_div)

            for hour in day:
                hour_div = s.new_tag('div')
                hour_div['class'] = hour_div.get('class', []) + [
                    'cell', 'course-container'
                ]
                for i, course in enumerate(hour):
                    course_div = course.to_html()
                    course_div['class'] = course_div.get('class',
                                                         []) + ['course']
                    if len(hour) > 1:
                        course_div['class'] = course_div.get('class',
                                                             []) + ['half']
                    if i == 0:
                        course_div['class'] = course_div.get('class', []) + [
                            'course-left'
                        ]
                    else:
                        course_div['class'] = course_div.get('class', []) + [
                            'course-right'
                        ]

                    if MERGE_CONSECUTIVE_COURSES:
                        if course.hours == 2:
                            course_div['class'] = course_div.get('class', []
                                                                ) + ['double']
                        if course.hours == 3:
                            course_div['class'] = course_div.get('class', []
                                                                ) + ['triple']
                        if course.delete:
                            course_div['class'] = course_div.get('class', []
                                                                ) + ['deleted']

                    hour_div.append(course_div)
                if len(hour) == 0:
                    hour_div['class'] = hour_div.get('class', []) + ['empty']
                elif len(hour) > 0 and all([course.delete for course in hour]):
                    hour_div['class'] = hour_div.get('class', []) + ['deleted']

                day_div.append(hour_div)

            new_soup.body.div.append(day_div)
        new_soup.head.insert(
            0,
            BeautifulSoup(
                '<link rel="stylesheet" href="stylesheet.css" type="text/css">',  # noqa: E501
                'html.parser'
            )
        )
        return new_soup

    @staticmethod
    def _string_to_courses(tags) -> List[Course]:
        courses = []
        if tags is []:
            return [Course(empty=True)]

        STATE_ROOM = 'STATE_ROOM'
        STATE_TYPE = 'STATE_TYPE'
        STATE_NAME = 'STATE_NAME'
        STATE_TEACHER = 'STATE_TEACHER'
        STATE_OTHER = 'STATE_OTHER'

        state = STATE_ROOM

        empty_course = {
            'room': None,
            'type': None,
            'name': None,
            'teacher': None,
            'other': None,
        }
        course = empty_course
        for tag in tags:
            while True:
                if tag.name == 'br':
                    break

                if isinstance(tag, NavigableString) and tag == ' ':
                    break

                if state == STATE_ROOM:
                    course.update({'room': tag.get_text()})
                    state = STATE_TYPE
                    break

                if state == STATE_TYPE:
                    course.update({'type': tag.get_text()})
                    state = STATE_NAME
                    break

                if state == STATE_NAME:
                    course.update({'name': tag.get_text()})
                    state = STATE_TEACHER
                    break

                if state == STATE_TEACHER:
                    course.update({'teacher': str(tag.string)})
                    state = STATE_OTHER
                    break

                if state == STATE_OTHER:
                    if re.compile(r'(EA|NE|AUD).*').match(tag.get_text()):
                        state = STATE_ROOM
                        continue
                    course.update({'other': tag.get_text()})
                    courses.append(course)
                    course = copy.deepcopy(empty_course)
                    state = STATE_ROOM
                    break

        if state == STATE_OTHER:
            courses.append(course)

        courses = [Course(dict_=c, empty=False) for c in courses]

        return courses
