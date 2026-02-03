# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import AreaMixin
import os
import csv
import re


def beach_codes():
    def decimal_degrees(pattern, degrees):
        res = pattern.match(degrees)
        sing_str = res.group(1)
        sign = -1 if sing_str == '-' else 1
        degrees = float(res.group(2))
        minutes = float(res.group(3))
        seconds = float(res.group(4))
        return sign * (degrees + minutes / 60 + seconds / 3600)

    degrees_pattern = r"(-?)(\d+)º (\d+)' (\d+)\""
    pattern = re.compile(degrees_pattern)
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'Playas_codigos.csv')
    with open(filepath, 'r', encoding='ISO-8859-15') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            yield {
                'id': row['ID_PLAYA'],
                'name': row['NOMBRE_PLAYA'],
                'province_id': row['ID_PROVINCIA'],
                'province_name': row['NOMBRE_PROVINCIA'],
                'municipality_id': row['ID_MUNICIPIO'],
                'municipality_name': row['NOMBRE_MUNICIPIO'],
                'latitude': decimal_degrees(pattern, row['LATITUD']),
                'longitude': decimal_degrees(pattern, row['LONGITUD']),
            }


class PredictionBeach(AreaMixin, Endpoint):
    beach_codes = staticmethod(beach_codes)

    def __init__(self, client):
        super(PredictionBeach, self).__init__(client)
        self._area = None

    @property
    def endpoint(self):
        if not self._area:
            raise ValueError("Area must have a value to obtain the beach prediction")
        return "prediccion/especifica/playa/{}".format(self._area)