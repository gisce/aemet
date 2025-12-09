# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests


class Aemet(object):
    """
    A wrapper for the AEMET OpenData API.
    Docs: https://opendata.aemet.es/dist/index.html
    """
    BASE_URL = "https://opendata.aemet.es/opendata/api/"

    def _clear(self):
        self._state = None
        self._description = None
        self._data = None
        self._data_url = None
        self._metadata = None
        self._metadata_url = None
        self._response_headers = None
        self._fetched.clear()

    def __init__(self, api_key, autofetch=False):
        self.api_key = api_key
        self.headers = {
            'cache-control': 'no-cache',
            'accept': 'application/json',
            'api_key': self.api_key
        }
        self._autofetch = autofetch
        self._fetched = set()
        self._clear()
        self._observations = None
        self._predictions = None

    def fetch(self):
        print("Fetching data from AEMET OpenData API...")
        self._clear()
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        self._response_headers = response.headers
        body = response.json()
        self._state = body.get('estado')
        self._description = body.get('description')
        if self._state == 200:
            self._data_url = body.get('datos')
            self._metadata_url = body.get('metadatos')

    def _do_autofetch(self, property_name):
        property_value = getattr(self, property_name)
        if not self._autofetch:
            if property_value is None:
                raise ValueError("The property doesn't have a value yet. Fetch it first!")
            return
        if (property_name[-4:] == '_url' and property_value is None and
                self._state and property_name not in self._fetched):
            pass
        elif property_value is None or property_name in self._fetched:
            if property_name in self._fetched:
                print("ReFetching {}".format(property_name))
            else:
                print("fetching {}".format(property_name))
            self.fetch()
            self._fetched.clear()
        self._fetched.add(property_name)

    def _to_json(self, request):
        return request.json()

    @property
    def base_url(self):
        return self.BASE_URL

    @property
    def endpoint(self):
        raise NotImplementedError("This class doesn't have an endpoint")

    @property
    def url(self):
        return self.base_url + self.endpoint

    @property
    def state(self):
        self._do_autofetch('_state')
        return self._state

    @property
    def description(self):
        self._do_autofetch('_description')
        return self._description

    @property
    def response_headers(self):
        self._do_autofetch('_response_headers')
        return self._response_headers

    @property
    def metadata_url(self):
        self._do_autofetch('_metadata_url')
        return self._metadata_url

    @property
    def metadata(self):
        if not self._autofetch:
            if self._metadata is None:
                if self._metadata_url is None:
                    raise ValueError("No url to fetch the metadata from")
                self._metadata = requests.get(self._metadata_url, headers=self.headers).json()
        else:
            if '_metadata' in self._fetched:
                self.fetch()
            if self._metadata is None:
                if self._metadata_url is None and self._state is None:
                    self.fetch()
                if self._metadata_url:
                    self._metadata = requests.get(self._metadata_url, headers=self.headers).json()
                    self._fetched.add('_metadata')
        return self._metadata

    @property
    def data_url(self):
        self._do_autofetch('_data_url')
        return self._data_url

    @property
    def data(self):
        if not self._autofetch:
            if self._data is None:
                if self._data_url is None:
                    raise ValueError("No url to fetch the data from")
                self._data = self._to_json(requests.get(self._data_url, headers=self.headers))
        else:
            if '_data' in self._fetched:
                self.fetch()
            if self._data is None:
                if self._data_url is None and self._state is None:
                    self.fetch()
                if self._data_url:
                    self._data = self._to_json(requests.get(self._data_url, headers=self.headers))
                    self._fetched.add('_data')
        return self._data

    @property
    def observations(self):
        if self._observations is None:
            from observations import Observations
            self._observations = Observations(self.api_key, autofetch=self._autofetch)
        return self._observations

    @property
    def predictions(self):
        if self._predictions is None:
            from aemet.predictions.predictions import Predictions
            self._predictions = Predictions(self.api_key, autofetch=self._autofetch)
        return self._predictions
