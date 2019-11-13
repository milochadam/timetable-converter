#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import copy
import json
import re
import sys
from parser import HTMLParser
from typing import List, Optional

from bs4 import BeautifulSoup, NavigableString
from course import Course
from settings import DAYS, ROOM_REGEX


def get_args():

    parser = argparse.ArgumentParser(
        description='Convert a timetable to a reasonable format.'
    )
    parser.add_argument(
        '-i',
        '--in',
        '--input',
        '--source',
        type=str,
        dest='source',
        default='SIS.html'
    )
    parser.add_argument(
        '-o',
        '--out',
        '--output',
        type=str,
        dest='output',
        default='SIS_out.html'
    )
    parser.add_argument('-m', '--move', type=str, dest='move', default='')
    return parser.parse_args(sys.argv[1:])


def main():
    args = get_args()
    soup = get_soup_from_file(args.source)

    new_soup = HTMLParser(soup=soup, moves=moves_to_json(args.move)).parse()

    save_html_file(new_soup, args.output)


def moves_to_json(moves: str) -> list:
    if not moves:
        return []

    def find_room(args: List[str]) -> str:
        for item in args:
            if ROOM_REGEX.match(item):
                return item
        return None

    def find_day(args: List[str]) -> str:
        for item in args:
            if item in DAYS:
                return DAYS.index(item) + 1
        return None

    def find_hour(args: List[str]) -> str:
        for item in args:
            try:
                return int(item)
            except ValueError:
                pass
        return None

    m = []
    for move in moves.split(';'):
        mf, mt = move.split('->')
        mf = mf.split(',')
        mt = mt.split(',')

        mtd = find_day(mt)
        mth = find_hour(mt)
        if mtd is None:
            mtd = find_day(mf)
        if mth is None:
            mth = find_hour(mf)
        m.append(
            [
                {
                    "room": find_room(mf),
                    "day": find_day(mf),
                    "hour": find_hour(mf),
                }, {
                    "day": mtd,
                    "hour": mth,
                }
            ]
        )

    return m


def get_soup_from_file(filename: str) -> BeautifulSoup:
    with open(filename) as f:
        html = f.read()
        return BeautifulSoup(html, 'html.parser')


def save_html_file(soup: BeautifulSoup, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(str(soup))


if __name__ == "__main__":
    main()
