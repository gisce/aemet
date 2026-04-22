# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import DayMixin

UVI_DAY_CODES = [
    (0, 'día actual'),
    (1, 'd+1 (mañana)'),
    (2, 'd+2 (pasado mañana)'),
    (3, 'd+3 (dentro de 3 días)'),
    (4, 'd+4 (dentro de 4 días)'),
]

_VALID_UVI_DAY_CODES = [udc[0] for udc in UVI_DAY_CODES]


class PredictionUvi(DayMixin, Endpoint):
    UVI_DAY_CODES = UVI_DAY_CODES

    def __init__(self, client):
        super(PredictionUvi, self).__init__(client)
        self._day = None

    @property
    def endpoint(self):
        if self._day not in _VALID_UVI_DAY_CODES:
            raise ValueError("Day must have a valid value to obtain the uvi prediction")
        return "prediccion/especifica/uvi/{}".format(self._day)