# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import AreaMixin

NIVOLOGY_AREA_CODES = [
    (0, 'Pirineo Catalán'),
    (1, 'Pirineo Navarro y Aragonés'),
]

_VALID_NIVOLOGY_AREA_CODES = [nac[0] for nac in NIVOLOGY_AREA_CODES]


class PredictionNivology(AreaMixin, Endpoint):
    NIVOLOGY_AREA_CODES = NIVOLOGY_AREA_CODES

    def __init__(self, client):
        super(PredictionNivology, self).__init__(client)
        self._area = None

    def _to_json(self, response):
        return response.text

    @property
    def endpoint(self):
        if self._area not in _VALID_NIVOLOGY_AREA_CODES:
            raise ValueError("Area must have a valid value to obtain the nivology prediction")
        return "prediccion/especifica/nivologica/{}".format(self._area)
