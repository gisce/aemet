# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.predictions.predictions import Predictions


class PredictionBeach(Predictions):
    @property
    def endpoint(self):
        if not self._area:
            raise ValueError("Area must have a value to obtain the beach prediction")
        return "prediccion/especifica/playa/{}".format(self._area)