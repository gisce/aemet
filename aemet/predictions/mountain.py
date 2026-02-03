# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import DayMixin, AreaMixin

MOUNTAIN_AREA_CODES = [
    ('peu1', 'Picos de Europa'),
    ('nav1', 'Pirineo Navarro'),
    ('arn1', 'Pirineo Aragonés'),
    ('cat1', 'Pirineo Catalán'),
    ('rio1', 'Ibérica Riojana'),
    ('arn2', 'Ibérica Aragonesa'),
    ('mad2', 'Sierras de Guadarrama y Somosierra'),
    ('gre1', 'Sierra de Gredos'),
    ('nev1', 'Sierra Nevada'),
]

_VALID_AREA_CODES = [mac[0] for mac in MOUNTAIN_AREA_CODES]

MOUNTAIN_DAY_CODES = [
    (0, 'día actual'),
    (1, 'd+1 (mañana)'),
    (2, 'd+2 (pasado mañana)'),
    (3, 'd+3 (siguente a pasado mañana)'),
]

_VALID_MOUNTAIN_DAY_CODES = [mdc[0] for mdc in MOUNTAIN_DAY_CODES]


class PredictionMountain(DayMixin, AreaMixin, Endpoint):
    MOUNTAIN_AREA_CODES = MOUNTAIN_AREA_CODES
    MOUNTAIN_DAY_CODES = MOUNTAIN_DAY_CODES

    def __init__(self, client):
        super(PredictionMountain, self).__init__(client)
        self._day = None
        self._area = None

    @property
    def endpoint(self):
        if self._area not in _VALID_AREA_CODES:
            raise ValueError("Area must have a valid value")
        if self._day in _VALID_MOUNTAIN_DAY_CODES:
            return "prediccion/especifica/montaña/pasada/area/{}/dia/{}".format(self._area, self._day)
        elif self._day:
            raise ValueError("Day must have a valid value to obtain the mountain prediction of that day")
        return "prediccion/especifica/montaña/pasada/area/{}".format(self._area)
