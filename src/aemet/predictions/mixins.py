# -*- coding: utf-8 -*-
from __future__ import absolute_import


class DayMixin(object):

    def day(self, day):
        if self._day != day:
            self._clear()
        self._day = day
        return self


class AreaMixin(object):

    def area(self, area):
        if self._area != area:
            self._clear()
        self._area = area
        return self
