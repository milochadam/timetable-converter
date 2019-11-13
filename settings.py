import re

ROOM_REGEX = re.compile('(NE|EA) ([0-9]{2,3}|AUD.+)')
TYPE_REGEX = re.compile('\[[WLPC]\]')
NAME_REGEX = re.compile('.{10,}')
INFO_REGEX = re.compile('(co .*|do .*|od .*)')
TEACHER_REGEX = re.compile('(mgr inż|dr (inż|hab)|prof).*')

HOUR = 'godz'
DAY1 = 'pn'
DAY2 = 'wt'
DAY3 = 'sr'
DAY4 = 'czw'
DAY5 = 'pt'

DAYS = [DAY1, DAY2, DAY3, DAY4, DAY5]
