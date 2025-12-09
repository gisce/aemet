# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.predictions.predictions import Predictions


class PredictionMunicipality(Predictions):
    def __init__(self, api_key, autofetch=False):
        super(PredictionMunicipality, self).__init__(api_key=api_key, autofetch=autofetch)
        self._daily = False
        self._hourly = False

    @property
    def daily(self):
        if self._daily == False:
            self._clear()
        self._daily = True
        self._hourly = False
        return self

    @property
    def hourly(self):
        if self._hourly == False:
            self._clear()
        self._daily = False
        self._hourly = True
        return self

    @property
    def endpoint(self):
        if not self._daily and not self._hourly:
            raise ValueError("Must declare whether the municipality prediction is daily or hourly")
        if self._daily:
            return "prediccion/especifica/municipio/diaria/{}".format(self._area)
        elif self._hourly:
            return "prediccion/especifica/municipio/horaria/{}".format(self._area)
        else:
            raise ValueError("The municipality endpoint can only be daily or hourly")