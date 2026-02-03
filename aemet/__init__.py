# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .client import Aemet
from .observations import MessageType
from .predictions.predictions import Predictions
from .predictions.uvi import UVI_DAY_CODES
from .predictions.nivology import NIVOLOGY_AREA_CODES
from .predictions.municipality import municipality_codes, municipality_search
from .predictions.mountain import MOUNTAIN_AREA_CODES, MOUNTAIN_DAY_CODES
from .predictions.municipality import get_municipality_info_ign_api, get_municipality_info_cartociudad_api
from .predictions.beach import beach_codes


__all__ = [
    'Aemet', 'MessageType', 'Predictions', 'UVI_DAY_CODES',
    'NIVOLOGY_AREA_CODES', 'municipality_codes', 'municipality_search',
    'MOUNTAIN_AREA_CODES', 'MOUNTAIN_DAY_CODES', 'beach_codes',
    'get_municipality_info_ign_api', 'get_municipality_info_cartociudad_api'
]
