# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import AreaMixin
from rapidfuzz import process, utils
import csv
import os
import datetime
import requests
from shapely.geometry import shape, Point


def municipality_codes():
    """
    municipality_codes are cpro (Province Code) + cmun (Municipality Code)
    :return:
    """
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'diccionario24.csv')
    with open(filepath, 'r', encoding='utf-8') as csv_file:
        next(csv_file)
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            yield {
                'codauto': row['CODAUTO'],  #autonomous comunity code
                'cpro': row['CPRO'],  # province code
                'cmun': row['CMUN'],  # municipality code
                'dc': row['DC'],  # control digit
                'name': row['NOMBRE'],
                'aemet_municipality_code': row['CPRO'] + row['CMUN'],
            }


def get_municipality_info_ign_api(name=None, lat=None, lon=None, skip_geometry=False):
    if name == lat == lon == None:
        raise ValueError("Must provide the 'name' or both 'lat' and 'lon' or all 3 parameters.")
    params = {
        'f': 'json',
        'lang': 'en',
        'limit': '10',
        'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84',  # results in lon lat, for lat lon -> 'http://www.opengis.net/def/crs/EPSG/0/4326'
        'properties': 'nationalcode,nameunit,nationallevelname',
        'skipGeometry': skip_geometry,
        'nationallevel': 'https://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/4thOrder',
    }
    if name is not None:
        params.update({'nameunit': name})
    if lat is not None and lon is not None:
        bbox = "{},{},{},{}".format(lon, lat, lon, lat)
        params.update({
            'bbox': bbox,
            'bbox-crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84',  # input in lon lat, for lat lon 'http://www.opengis.net/def/crs/EPSG/0/4326'
        })
    response = requests.get(
        'https://api-features.ign.es/collections/administrativeunit/items',
        params=params
    )
    pt = Point(lon, lat)
    municipalities = {}
    for feature in response.json().get('features', []):
        geometry = feature.get('geometry')
        props = feature['properties']
        if geometry:
            geom = shape(geometry)
            if geom.contains(pt):
                municipalities[props['nameunit']] = props['nationalcode'][-5:]
        else:
            municipalities[props['nameunit']] = props['nationalcode'][-5:]
    return municipalities


def get_municipality_info_cartociudad_api(lat, lon):
    params = {'lat': lat, 'lon': lon}
    r = requests.get(
        'https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode',
        params=params,
    )
    r.raise_for_status()
    return r.json()


def municipality_search(query, limit=5, score_cutoff=60):
    """
    Performs a fuzzy search and returns the best matches.
    :param query: The name to search for (e.g., 'Giron')
    :param limit: How many results to return
    :param score_cutoff: Minimum similarity (0-100)
    """
    municipalities = list(municipality_codes())
    names = [m['name'] for m in municipalities]

    matches = process.extract(
        query,
        names,
        processor=utils.default_process,  # Handles lowercase/accents
        limit=limit,
        score_cutoff=score_cutoff
    )

    results = []
    for name, score, index in matches:
        results.append({
            'match': municipalities[index],
            'confidence': score
        })
    return results


class PredictionMunicipality(AreaMixin, Endpoint):
    """
    Aemet Municipality Code is the CPRO (Province Code) + CMUN (Municipality Code)
    """
    municipality_codes = staticmethod(municipality_codes)
    get_municipality_info_ign_api = staticmethod(get_municipality_info_ign_api)
    get_municipality_info_cartociudad_api = staticmethod(get_municipality_info_cartociudad_api)
    municipality_search = staticmethod(municipality_search)

    # https://web2.aemet.es/es/eltiempo/prediccion/municipios/banyoles-id17015/ayuda, https://web2.aemet.es/es/eltiempo/prediccion/municipios/horas/banyoles-id17015
    # todo: wind is given in the website as [0,1],the end is 1, that I give it with a 0
    # todo: different from thre rest, given in as [0,1] the end is 1 (10 min), and I give it as 1
    # todo: fix it
    def __init__(self, client):
        super(PredictionMunicipality, self).__init__(client)
        self._area = None
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

    def municipality(self, code):
        self.area(code)
        return self

    @property
    def endpoint(self):
        if not self._daily and not self._hourly:
            raise ValueError("Must declare whether the municipality prediction is daily or hourly")
        if self._daily:
            return "prediccion/especifica/municipio/diaria/{}".format(self._area)
        else:
            return "prediccion/especifica/municipio/horaria/{}".format(self._area)


    @staticmethod
    def parse_period(period):
        elements = period.split('-')
        if len(elements) == 1 and len(period) == 4:
            elements = period[0:2], period[2:4]
        if len(elements) == 1:
            start = int(period)
            end = start + 1
        else:
            start, end = elements
        start, end = int(start), int(end)
        if end < start:
            end += 24
        return start, end

    def get_period_values(self, period_list):
        res = {}
        if isinstance(period_list, dict):
            max = period_list.get('maxima')
            min = period_list.get('minima')
            datos = period_list.get('dato', [])
            len_datos = len(datos) or 1
            hour_diff = int(24 / len_datos)
            res = {}
            for dato in datos:
                hour_range = dato.get('hora')
                for hour in range(hour_range-hour_diff, hour_range):
                    res[hour] = {'value': dato.get('value')}
            res['max'] = max
            res['min'] = min
        elif isinstance(period_list, (list, tuple)):
            if len(period_list) == 1:
                item = period_list[0]
                for hour in range(0, 24):
                    res[hour] = item
            else:
                for p in period_list:
                    p['periodo'] = self.parse_period(p['periodo'])
                sorted_period_list = sorted(period_list, key=lambda d: ((d['periodo'][1]-d['periodo'][0]), d['periodo'][0]))
                for item in sorted_period_list:
                    for hour in range(item['periodo'][0], item['periodo'][1]):
                        if hour not in res:
                            res[hour] = {k: v for k, v in item.items() if k != 'periodo'}
        return res

    @property
    def values(self):
        data = self._data if self._data else self.data
        res = []
        for element in data:
            parsed_data = element.copy()
            parsed_data.pop('prediccion')
            for key, values in element['prediccion'].items():
                week_values = {}
                for value in values:
                    date = None
                    day_values = {}
                    for k, v in value.items():
                        if k in 'fecha':
                            date = v
                        elif k == 'uvMax':
                            day_values.update({k: {'max': v}})
                        elif k in ('orto', 'ocaso'):
                            day_values.update({k: v})
                        else:
                            day_values.update({k: self.get_period_values(v)})
                    week_values.update({date: day_values})
                parsed_data['data'] = week_values
            res.append(parsed_data)
        return res
