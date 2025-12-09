# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.predictions.predictions import Predictions


class PredictionUvi(Predictions):
    @property
    def endpoint(self):
        if not self._day:
            raise ValueError("Day must have a value to obtain the uvi prediction")
        return "prediccion/especifica/uvi/{}".format(self._day)