# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
from aemet.predictions.mixins import AreaMixin
from rapidfuzz import process, utils
import csv
import os
import requests
from shapely.geometry import shape, Point
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import functools

SINGLE = 0
RANGE = 1
COMPACT_RANGE = 2


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


#  https://www.cartociudad.es/web/portal/directorio-de-servicios/geoprocesamiento
def get_municipality_info_cartociudad_api(lat, lon):
    params = {'lat': lat, 'lon': lon}
    r = requests.get(
        'https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode',
        params=params,
    )
    r.raise_for_status()
    return r.json()


# https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCoordenadas.svc/json/help
def get_municipality_info_catastro_api(lat, lon):
    r = requests.get(
        'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/'
        'COVCCoordenadas.svc/json/Consulta_RCCOOR_Distancia'
        '?CoorX={COORX}&CoorY={COORY}&SRS={SRS}'.format(
            COORX=lon, COORY=lat, SRS='EPSG:4326'
        )
    )
    r.raise_for_status()
    return r.json()


# https://github.com/pelias/documentation/
def get_municipality_info_geolocalizador_idee(lat, lon):
    r = requests.get(
        'https://geolocalizador.idee.es/v1/reverse'
        '?point.lat={lat}&point.lon={lon}&size=1'.format(
            lat=lat, lon=lon
        )
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
    get_municipality_info_catastro_api = staticmethod(get_municipality_info_catastro_api)
    get_municipality_info_geolocalizador_idee = staticmethod(get_municipality_info_geolocalizador_idee)
    municipality_search = staticmethod(municipality_search)

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
    def parse_period(period, period_type='SINGLE'):
        if isinstance(period, tuple) and len(period) == 2:
            return period

        if period_type == SINGLE:  # single int in str format
            start = int(period)
            end = start + 1

        elif period_type == RANGE:  # two ints separated by '-'
            start, end = period.split('-')

        elif period_type == COMPACT_RANGE:  # two str ints both of size 2
            start, end = period[0:2], period[2:4]

        start, end = int(start), int(end)

        if end < start:
            end += 24
        return start, end

    @staticmethod
    def _generate_hourly_timestamps(date: str) -> list[datetime]:
        base_dt = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
        return [base_dt + timedelta(hours=i) for i in range(1, 25)]

    def get_period_values_minmax(self, period_list):
        res = {'values': [None] * 24, 'minmax': {}}
        res['minmax']['max'] = period_list.get('maxima')
        res['minmax']['min'] = period_list.get('minima')

        datos = period_list.get('dato', [])
        len_datos = len(datos) or 1
        hour_diff = int(24 / len_datos)
        for dato in datos:
            hour_range = dato.get('hora')
            for hour in range(hour_range-hour_diff, hour_range):
                res['values'][hour] = dato['value']
        return res

    def get_period_values_list(self, period_list, period_type):
        for p in period_list:
            p['periodo'] = self.parse_period(p['periodo'], period_type=period_type)
        sorted_period_list = sorted(period_list, key=lambda d: ((d['periodo'][1]-d['periodo'][0]), d['periodo'][0]))
        range_values = max(24, sorted_period_list[-1]['periodo'][1])
        res = [None] * range_values
        for item in sorted_period_list:
            for hour in range(item['periodo'][0], item['periodo'][1]):
                if res[hour] is None:
                    res[hour] = item['value']
        return res

    def get_period_values_int(self, period_list):
        return [period_list[0]['value']] * 24  # no period in the peirod_list


    @property
    def values(self):
        data = self._data if self._data else self.data
        if self._daily:
            res = self._get_daily_data(data)
        elif self._hourly:
            res = self._get_hourly_data(data)
        else:
            raise ValueError("Must declare whether the municipality prediction is daily or hourly")
        return res

    def _get_predictions(self, data):
        if not data:
            return []

        element = data[0]
        prediccion = element.get('prediccion')
        if not prediccion:
            return []

        weekly_values = prediccion['dia']
        if not weekly_values:
            return []

        return weekly_values

    def _get_daily_data(self, data):
        weekly_values = self._get_predictions(data)

        rwv = defaultdict(list)  # response weekly values
        rwv_minmax = {}  # response weekly values minmax fields
        for day, day_values in enumerate(weekly_values):  # goes though the days in order
            if day <= 3:
                get_vals = functools.partial(self.get_period_values_list, period_type=RANGE)
            else:
                get_vals = self.get_period_values_int
            date = None
            rdv_minmax = {}  # response daily values minmax fields
            for field, val in day_values.items():
                if field in 'fecha':
                    date = val
                elif field == 'uvMax':
                    rdv_minmax.update({field: {'max': val}})
                elif field in ('viento'):
                    vv_val = [{'value': v.get('velocidad'), 'periodo': v.get('periodo')} for v in val]
                    dv_val = [{'value': v.get('direccion'), 'periodo': v.get('periodo')} for v in val]
                    rwv['velocidadViento'].extend(get_vals(vv_val))
                    rwv['direccionViento'].extend(get_vals(dv_val))
                elif field in ('temperatura', 'sensTermica', 'humedadRelativa'):
                    values = self.get_period_values_minmax(val)
                    rwv[field].extend(values['values'])
                    rdv_minmax.update({field: values['minmax']})
                elif field in ('probPrecipitacion', 'cotaNieveProv', 'estadoCielo', 'rachaMax'):
                    rwv[field].extend(get_vals(val))
                else:
                    raise Exception("Field {} hasn't been taken into account".format(field))
            rwv['fecha'].extend(self._generate_hourly_timestamps(date))
            rwv_minmax.update({date: rdv_minmax})

        return rwv, rwv_minmax

    def _get_hourly_data(self, data):
        weekly_values = self._get_predictions(data)

        rwv = defaultdict(list)
        rwv_minmax = {}
        for day, day_values in enumerate(weekly_values):
            date = None
            rdv_minmax = {}
            for field, val in day_values.items():
                if field in 'fecha':
                    date = val
                elif field in ('orto', 'ocaso'):
                    rdv_minmax.update({field: val})
                elif field in ('vientoAndRachaMax',):
                    racha_max_val = [d for d in val if len(d) == 2]
                    viento_val = [d for d in val if len(d) == 3]
                    dv_val = [{'value': v.get('direccion', [None])[0], 'periodo': v.get('periodo')} for v in viento_val]
                    vv_val = [{'value': v.get('velocidad', [None])[0], 'periodo': v.get('periodo')} for v in viento_val]
                    rwv['velocidadViento'].extend(self.get_period_values_list(vv_val, period_type=SINGLE))
                    rwv['direccionViento'].extend(self.get_period_values_list(dv_val, period_type=SINGLE))
                    rwv['rachaMax'].extend(self.get_period_values_list(racha_max_val, period_type=SINGLE))
                elif field in ('probPrecipitacion', 'probTormenta', 'probNieve'):
                    values = self.get_period_values_list(val, period_type=COMPACT_RANGE)
                    if day > 0:
                        values = values[2:]
                    rwv[field].extend(values)
                elif field in ('estadoCielo', 'precipitacion', 'nieve', 'temperatura', 'sensTermica', 'humedadRelativa'):
                    rwv[field].extend(self.get_period_values_list(val, period_type=SINGLE))
                else:
                    raise Exception("Field {} hasn't been taken into account".format(field))
            rwv['fecha'].extend(self._generate_hourly_timestamps(date))
            rwv_minmax.update({date: rdv_minmax})
        return rwv, rwv_minmax
