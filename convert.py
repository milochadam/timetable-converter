#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import re
import sys

source = "SIS.html"
output = "out.html"
if len(sys.argv) > 2:
    source = str(sys.argv[1])
    output = str(sys.argv[2])

def main():
    # print("main")
    soup = get_html_file(source)
    parser = HTMLparser(soup)
    parser.modify_soup()
    save_html_file(parser.soup, output)


def get_html_file(filename):
    with open(filename) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, "html.parser")
    return soup


def save_html_file(soup, filename):
    with open(filename, "w") as outf:
        outf.write(str(soup))


class HTMLparser():
    def __init__(self, soup):
        self.soup = soup

    def modify_soup(self):
        self.remove_common_terms()
        self.remove_clutter()
        self.add_stylesheet()
        self.add_classes()
        self.add_js_stuff()

    def add_js_stuff(self):
        self.soup.head.append(bs4.BeautifulSoup(
            '<script type="text/javascript" src="scripts.js"></script>', "html.parser"))
        self.soup.body['onload'] = 'enable_all()'
        root = self.soup.find('div', {'class': 'blue_div'})
        js_root = self.soup.new_tag('div')
        root.append(js_root)
        button_div = self.soup.new_tag('div')
        button_div['class'] = 'button_div'
        js_root.append(button_div)

        self.add_button(button_div, 'toggle lectures',  'lecture')
        self.add_button(button_div, 'toggle labs', 'lab')
        self.add_button(button_div, 'toggle projects', 'project')
        self.add_button(button_div, 'toggle exercises', 'exercise')
        self.add_button(button_div, 'toggle last-10', 'last-10-weeks')
        self.add_button(button_div, 'do 29.11/30.11', 'do-29-11')

    def add_button(self, root, text, id_):
        button = self.soup.new_tag('button')
        button.append(text)
        button['class'] = button.get('class', [])+['toggle_button']
        button['id'] = id_
        root.append(button)

    def add_stylesheet(self):
        self.soup.head.append(bs4.BeautifulSoup(
            '<link rel="stylesheet" type="text/css" href="stylesheet.css">', "html.parser"))

    def add_classes(self):
        self.add_class_for_text_grandparent('\[W\]', 'lecture')
        self.add_class_for_text_grandparent('\[L\]', 'lab')
        self.add_class_for_text_grandparent('\[P\]', 'project')
        self.add_class_for_text_grandparent('\[C\]', 'exercise')
        self.add_class_for_text_parent('[0-9]{1,2}:[0-9]{1,2}', 'hour')
        self.add_class_for_text_grandparent('ostatnie', 'last-10-weeks')
        self.add_class_for_text_grandparent('29|30\.', 'do-29-11')

    def add_class_for_text_grandparent(self, text, css_class):
        for elem in self.soup(text=re.compile(text)):
            parent = elem.parent.parent
            parent['class'] = parent.get('class', [])+[css_class]

    def add_class_for_text_parent(self, text, css_class):
        for elem in self.soup(text=re.compile(text)):
            parent = elem.parent
            parent['class'] = parent.get('class', [])+[css_class]

    def remove_common_terms(self):
        terminy_wspolne = self.soup.find_all('b', text=re.compile("termin"))
        for term in terminy_wspolne:
            self.remove_common_term(term)

    def remove_common_term(self, endpoint):
        current = endpoint
        parent = current.parent
        for _ in range(9):
            current = self.remove_element(current)

        if len(parent.contents) > 0:
            child = parent.contents[0]
            if child.name == 'br':
                child.extract()

    def remove_element(self, text):
        """Removes element and returns previous sibling if exists"""
        ret_value = text.previous_sibling
        text.extract()
        return ret_value

    def remove_clutter(self):
        self.soup.html.attrs = None
        self.remove_all_tags('script')
        self.remove_all_tags('style')
        self.remove_all_tags('link')
        self.remove_all_tags('footer')
        self.soup.find('div', class_="navbar").extract()
        self.soup.find('div', class_="white_radius_div_center").extract()
        self.soup.find('div', class_="center-div").extract()
        for tag in self.soup.find_all(['th', 'tr', 'td'], attrs={'style': re.compile("background-color.*")}):
            del tag['style']
        for row in self.soup.find_all('tr'):
            if len(row.text) < 51:
                row.extract()

    def remove_all_tags(self, tag_name):
        result = self.soup.find_all(tag_name)
        for res in result:
            res.extract()


if __name__ == "__main__":
    main()
