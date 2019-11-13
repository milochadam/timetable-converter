from typing import Optional

from bs4 import BeautifulSoup


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

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

        name_type_container = s.new_tag(
            'div', attrs={'class': 'name-type-container'}
        )
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
