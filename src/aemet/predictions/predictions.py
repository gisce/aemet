# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.uvi import PredictionUvi
from aemet.predictions.beach import PredictionBeach
from aemet.predictions.municipality import PredictionMunicipality
from aemet.predictions.nivology import PredictionNivology
from aemet.predictions.mountain import PredictionMountain


class Predictions(object):
    def __init__(self, client):
        self.beach = PredictionBeach(client)
        self.mountain = PredictionMountain(client)
        self.municipality = PredictionMunicipality(client)
        self.nivology = PredictionNivology(client)
        self.uvi = PredictionUvi(client)
