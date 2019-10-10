#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import re
import argparse
import sys
from bs4 import BeautifulSoup, NavigableString
from typing import List, Optional


parser = argparse.ArgumentParser(description='Convert a timetable to a reasonable format.')
parser.add_argument('-i', '--in', '--input', '--source', type=str, dest='source', default='SIS.html')
parser.add_argument('-o', '--out', '--output', type=str, dest='output', default='SIS_out.html')
args = parser.parse_args(sys.argv[1:])

DAY_NAMES_PRESENT = True
DAYS = 5
HOURS = 15
WEEKDAY_NAMES = [
    'Poniedziałek',
    'Wtorek',
    'Środa',
    'Czwartek',
    'Piątek',
]
MERGE_CONSECUTIVE_COURSES = True


def main():
    soup = get_soup_from_file(args.source)
    parser = HTMLParser(soup)
    new_soup = parser.main()
    output = args.output
    save_html_file(new_soup, output)


def get_soup_from_file(filename: str) -> BeautifulSoup:
    with open(filename) as f:
        html = f.read()
        return BeautifulSoup(html, 'html.parser')


def save_html_file(soup: BeautifulSoup, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(str(soup))


class Course:
    def __init__(self, dict_: Optional[dict] = None, empty=True):
        self.empty = empty
        self.room = None
        self.type = None
        self.name = None
        self.teacher = None
        self.other = None

        self.hours = 1
        self.checked = False
        self.delete = False
        if dict_:
            for k, v in dict_.items():
                setattr(self, k, v)

    def __eq__(self, other: 'Course'):
        return self.room == other.room and \
               self.type == other.type and \
               self.name == other.name and \
               self.teacher == other.teacher and \
               self.other == other.other

    def to_html(self):
        s = BeautifulSoup('', 'html.parser')
        container = s.new_tag('div')
        types = {
            '[W]': 'lecture',
            '[P]': 'project',
            '[L]': 'laboratory',
            '[C]': 'exercise',
            '[S]': 'seminar',
        }
        room_tag = s.new_tag('div', attrs={'class': 'room'})
        room_tag.string = self.room

        # type
        container['class'] = container.get('class', []) + [types[self.type]]

        name_type_container = s.new_tag('div', attrs={'class': 'name-type-container'})
        type_tag = s.new_tag('span', attrs={'class': 'type'})
        type_tag.string = self.type
        name_tag = s.new_tag('span', attrs={'class': 'name'})
        name_tag.string = self.name
        name_type_container.append(type_tag)
        name_type_container.append(name_tag)

        teacher_tag = s.new_tag('div', attrs={'class': 'teacher'})
        teacher_tag.string = self.teacher

        container.insert(0, room_tag)
        # container.insert(1, type_tag)
        container.insert(2, name_type_container)
        container.insert(3, teacher_tag)
        if self.other:
            other_tag = s.new_tag('div', attrs={'class': 'other'})
            other_tag.string = self.other
            container.insert(4, other_tag)
        return container


class HTMLParser:

    def __init__(self, soup) -> None:
        self.soup = soup

    def main(self) -> BeautifulSoup:
        new_plan = [[[] for y in range(HOURS)]
            for x in range(DAYS)]
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
                # print(courses)

        if MERGE_CONSECUTIVE_COURSES:
            for day in new_plan:
                for y, hour in enumerate(day):
                    if hour is []:
                        continue
                    for course in hour:
                        if course.checked:
                            course.delete = True
                            continue
                        next_hours = day[y+1:]
                        for next_hour in next_hours:
                            matching_course = [c for c in next_hour if course == c]
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
        timetable_div['class'] = timetable_div.get('class', []) + ['timetable-container']
        new_soup.body.insert(0, timetable_div)
        hours_div = s.new_tag('div')
        for i in range(HOURS):
            hour_div = s.new_tag('div')
            hour_div['class'] = hour_div.get('class', []) + ['cell', 'hour']
            hour_div.string = f'{i + 7}:00'
            hours_div.append(hour_div)
        if DAY_NAMES_PRESENT:
            empty_cell = s.new_tag('div')
            empty_cell['class'] = empty_cell.get('class', []) + ['cell', 'empty-in-corner']
            hours_div.insert(0, empty_cell)
        timetable_div.insert(0, hours_div)
        for day_number, day in enumerate(new_plan):
            day_div = s.new_tag('div')
            day_div['class'] = day_div.get('class', []) + ['day']
            if DAY_NAMES_PRESENT:
                day_name_div = s.new_tag('div')
                day_name_div.string = WEEKDAY_NAMES[day_number]
                day_name_div['class'] = day_name_div.get('class', []) + ['day-name']
                day_div.append(day_name_div)

            for hour in day:
                hour_div = s.new_tag('div')
                hour_div['class'] = hour_div.get('class', []) + ['cell', 'course-container']
                for i, course in enumerate(hour):
                    course_div = course.to_html()
                    course_div['class'] = course_div.get('class', []) + ['course']
                    if len(hour) > 1:
                        course_div['class'] = course_div.get('class', []) + ['half']
                    if i == 0:
                        course_div['class'] = course_div.get('class', []) + ['course-left']
                    else:
                        course_div['class'] = course_div.get('class', []) + ['course-right']

                    if MERGE_CONSECUTIVE_COURSES:
                        if course.hours == 2:
                            course_div['class'] = course_div.get('class', []) + ['double']
                        if course.hours == 3:
                            course_div['class'] = course_div.get('class', []) + ['triple']
                        if course.delete:
                            course_div['class'] = course_div.get('class', []) + ['deleted']

                    hour_div.append(course_div)
                if len(hour) == 0:
                    hour_div['class'] = hour_div.get('class', []) + ['empty']
                elif len(hour) > 0 and all([course.delete for course in hour]):
                    hour_div['class'] = hour_div.get('class', []) + ['deleted']

                day_div.append(hour_div)

            new_soup.body.div.append(day_div)
        new_soup.head.insert(0, BeautifulSoup('<link rel="stylesheet" href="stylesheet.css" type="text/css">', 'html.parser'))
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


if __name__ == "__main__":
    main()
