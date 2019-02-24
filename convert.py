#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import re
import sys
from pdb_clone import pdb

source = "SIS.html"
output = "out.html"
if len(sys.argv) > 2:
    source = str(sys.argv[1])
    output = str(sys.argv[2])

ROOM_REGEX = re.compile('(NE|EA) ([0-9]{2,3}|AUD.+)')
TYPE_REGEX = re.compile('\[[WLPC]\]')
NAME_REGEX = re.compile('.{10,}')
INFO_REGEX = re.compile('(co .*|do .*|od .*)')
TEACHER_REGEX = re.compile('(mgr inż|dr (inż|hab)|prof).*')



class Cell:
    def __init__(self, rowspan=True):
        self.cell = self.new_tag('td')
        self.cell['rowspan'] = 2

    def get_object(self):
        return self.cell

    def new_tag(self, name):
        return bs4.BeautifulSoup("","html.parser").new_tag(name)

class HourCell(Cell):
    def __init__(self, hour):
        super().__init__()
        self.hour = hour

    def get_object(self):
        self.cell.string = self.hour
        self.cell['class'] = 'hour'
        return self.cell


class EmptyCell(Cell):
    pass

class TitleCell(Cell):
    def __init__(self, string):
        super().__init__()
        self.string = string

    def get_object(self):
        self.cell.string = self.string
        self.cell['class'] = 'weekday'
        return self.cell


class LessonCell(Cell):
    COLOR_SWITCHER = {
        '[W]': 'lecture',
        '[C]': 'exercise',
        '[P]': 'project',
        '[L]': 'labs',
    }
    def __init__(self, dic, double_span=True):
        super().__init__()
        self._classroom = dic['room']
        self._type = dic['type']
        self._name = dic['name']
        self._teacher = dic['teacher']
        self._info = dic['info']
        self.double_span = double_span

    def get_object(self):
        if not self.double_span:
            self.cell['rowspan'] = 1

        tag_room = self.new_tag('div')
        tag_room.string = self._classroom
        tag_room['class'] = ['lesson-room']

        tag_name = self.new_tag('div')
        tag_name.string = self._type + self._name
        tag_name['class'] = ['lesson-name']

        tag_teacher = self.new_tag('div')
        tag_teacher.string = self._teacher

        tag_info = self.new_tag('div')
        tag_info.string = self._info if self._info is not None else ""
        tag_info['class'] = ['lesson-info']

        self.cell.append(tag_room)
        # self.cell.append(tag_type)
        self.cell.append(tag_name)
        self.cell.append(tag_teacher)
        self.cell.append(tag_info)

        self._set_attrs()
        return self.cell

    def _set_attrs(self):
        self.cell['class'] = self.cell.get('class', []) + ['lesson', self.COLOR_SWITCHER[self._type]]


def main():
    soup = get_html_file(source)
    parser = HTMLparser(soup)
    parser.modify_soup()
    save_html_file(parser.out_soup, output)


def get_html_file(filename):
    with open(filename) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, "html.parser")
    return soup


def save_html_file(soup, filename):
    with open(filename, "w") as outf:
        outf.write(soup.prettify())


class HTMLparser():
    def __init__(self, soup):
        self.soup = soup
        self.out_soup = bs4.BeautifulSoup('<head></head><body></body>', 'html.parser')

    def modify_soup(self):
        self.init_table()
        self.add_links()

    def init_table(self):
        tab = [[
            TitleCell(''),
            TitleCell('Poniedziałek'),
            TitleCell('Wtorek'),
            TitleCell('Środa'),
            TitleCell('Czwartek'),
            TitleCell('Piątek'),
        ]]
        table = self.soup.find('table')
        trs = table.find_all('tr')
        for tr in trs:
            overflow = []
            tab.append([])
            tds = tr.find_all('td')
            for td in tds:
                if td.string != None:
                    tab[-1].append(HourCell(td.string))
                else:
                    l = len(td)
                    if l == 0:
                        tab[-1].append(EmptyCell())
                        continue

                    contents = td.contents

                    dic, index = self.parse_cell(contents, 0)

                    if index < l:
                        tab[-1].append(LessonCell(dic, False))
                        dic2, index2, = self.parse_cell(contents, index-4)
                        overflow.append(LessonCell(dic2, False))
                        continue

                    tab[-1].append(LessonCell(dic, True))
            if overflow != []:
                tab.append(overflow)

        table = self.soup.new_tag('table')
        for row in tab:
            new_row = self.soup.new_tag('tr')
            for cell in row:
                new_row.append(cell.get_object())

            rowspan2_count = len(new_row.find_all(rowspan=2))
            if rowspan2_count == 6:
                for cell in new_row:
                    cell.attrs.pop('rowspan')
            table.append(new_row)

        self.out_soup.body.append(table)


    def parse_cell(self, node_list, index):
        ROOM = 'room'
        TYPE = 'type'
        NAME = 'name'
        INFO = 'info'
        TEACHER = 'teacher'

        ret_dict = {
            'room': None,
            'type': None,
            'name': None,
            'teacher': None,
            'info': None,
        }

        STATE = ROOM
        info_try_count = 0
        for item in node_list[index:]:
            index += 1
            if item.string == None:
                continue

            if info_try_count == 2:
                break

            if STATE == INFO:
                info_try_count += 1
                if INFO_REGEX.match(item.string):
                    ret_dict['info'] = item.string
                continue

            if STATE == TEACHER:
                if NAME_REGEX.match(item.string):
                    ret_dict['teacher'] = item.string
                    STATE = INFO
                    continue

            if STATE == NAME:
                if NAME_REGEX.match(item.string):
                    ret_dict['name'] = item.string
                    STATE = TEACHER
                    continue

            if STATE == TYPE:
                if TYPE_REGEX.match(item.string):
                    ret_dict['type'] = item.string
                    STATE = NAME
                    continue

            if STATE == ROOM:
                try:
                    if 'room_name' in item.contents[0]['class']:
                        ret_dict['room'] = item.contents[0].string
                        STATE = TYPE
                        continue
                except (TypeError) as e:
                    ret_dict['room'] = item.string
                    STATE = TYPE
                    continue
                except Exception as e:
                    print(type(e).__name__)
                    print(item)
                    pass
        return ret_dict, index


    def add_links(self):
        self.out_soup.head.append(bs4.BeautifulSoup(
            '<meta charset="utf-8">', "html.parser"))
        self.out_soup.head.append(bs4.BeautifulSoup(
            '<link rel="stylesheet" type="text/css" href="stylesheet.css">', "html.parser"))


if __name__ == "__main__":
    main()
