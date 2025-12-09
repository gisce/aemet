# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.predictions.predictions import Predictions


class PredictionMountain(Predictions):
    @property
    def endpoint(self):
        if not self._area:
            raise ValueError("Area must have a value")
        if self._day:
            return "prediccion/especifica/montaña/pasada/area/{}/dia/{}".format(self._area, self._day)
        return "prediccion/especifica/montaña/pasada/area/{}".format(self._area)
