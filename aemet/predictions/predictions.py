# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.service import Aemet


class Predictions(Aemet):
    def __init__(self, api_key, autofetch=False):
        super(Predictions, self).__init__(api_key=api_key, autofetch=autofetch)
        self._area = None
        self._day = None
        self._mountain = None
        self._nivology = None
        self._municipality = None
        self._beach = None
        self._uvi = None

    def area(self, area):
        if self._area != area:
            self._clear()
        self._area = area
        return self

    def day(self, day):
        if self._day != day:
            self._clear()
        self._day = day
        return self

    @property
    def mountain(self):
        if self._mountain is None:
            from aemet.predictions.mountain import PredictionMountain
            self._mountain = PredictionMountain(self.api_key, autofetch=self._autofetch)
        return self._mountain

    @property
    def nivology(self):
        if self._nivology is None:
            from aemet.predictions.nivology import PredictionNivology
            self._nivology = PredictionNivology(self.api_key, autofetch=self._autofetch)
        return self._nivology

    @property
    def municipality(self):
        if self._municipality is None:
            from aemet.predictions.municipality import PredictionMunicipality
            self._municipality = PredictionMunicipality(self.api_key, autofetch=self._autofetch)
        return self._municipality

    @property
    def beach(self):
        if self._beach is None:
            from aemet.predictions.beach import PredictionBeach
            self._beach = PredictionBeach(self.api_key, autofetch=self._autofetch)
        return self._beach

    @property
    def uvi(self):
        if self._uvi is None:
            from aemet.predictions.uvi import PredictionUvi
            self._uvi = PredictionUvi(self.api_key, autofetch=self._autofetch)
        return self._uvi
