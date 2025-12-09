# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.predictions.predictions import Predictions


class PredictionNivology(Predictions):
    @property
    def endpoint(self):
        if not self._area:
            raise ValueError("Area must have a value to obtain the nivology prediction")
        return "prediccion/especifica/nivologica/{}".format(self._area)
