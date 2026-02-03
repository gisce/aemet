# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.observations import Observations
from aemet.predictions.predictions import Predictions


class Aemet(object):
    BASE_URL = "https://opendata.aemet.es/opendata/api/"

    def __init__(self, api_key, autofetch=False):
        self.api_key = api_key
        self.autofetch = autofetch
        self.headers = {
            'cache-control': 'no-cache',
            'accept': 'application/json',
            'api_key': self.api_key
        }
        self.observations = Observations(self)
        self.predictions = Predictions(self)
