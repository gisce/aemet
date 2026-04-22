# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests


class Endpoint(object):
    def __init__(self, client):
        self.client = client
        self._accessed = set()

        self._state = None
        self._description = None
        self._response_headers = None
        self._data_url = None
        self._metadata_url = None
        self._data = None
        self._metadata = None

    def _clear(self):
        self._accessed.clear()
        self._data = None
        self._metadata = None

        self._response_headers = None
        self._state = None
        self._description = None
        self._data_url = None
        self._metadata_url = None

    def _to_json(self, response): return response.json()
    @property
    def base_url(self): return self.client.BASE_URL
    @property
    def endpoint(self): raise NotImplementedError("This class doesn't have an endpoint")
    @property
    def url(self): return self.base_url + self.endpoint
    @property
    def response_headers(self): return self._get_val('response_headers', self._response_headers)
    @property
    def state(self): return self._get_val('state', self._state)
    @property
    def description(self): return self._get_val('description', self._description)
    @property
    def data_url(self): return self._get_val('data_url', self._data_url)
    @property
    def metadata_url(self): return self._get_val('metadata_url', self._metadata_url)
    @property
    def data(self): return self._get_complex_val('data', self._data)
    @property
    def metadata(self): return self._get_complex_val('metadata', self._metadata)

    def fetch(self):
        """Fetches the simple params"""
        self._accessed.clear()
        self._data = None
        self._metadata = None
        response = requests.get(self.url, headers=self.client.headers)
        response.raise_for_status()
        self._response_headers = response.headers
        body = response.json()
        self._state = body.get('estado')
        self._description = body.get('descripcion')
        if self._state == 200:
            self._data_url = body.get('datos')
            self._metadata_url = body.get('metadatos')

    def fetch_data(self):
        if not self._data_url:
            if self.client.autofetch: self.fetch()
            else: raise ValueError("data_url is None. Call fetch() first.")
        data = requests.get(self._data_url, headers=self.client.headers)
        data.raise_for_status()
        self._data = self._to_json(data)
        return self._data

    def fetch_metadata(self):
        if not self._metadata_url:
            if self.client.autofetch: self.fetch()
            else: raise ValueError("metadata_url is None. Call fetch() first.")
        metadata = requests.get(self._metadata_url, headers=self.client.headers)
        metadata.raise_for_status()
        self._metadata = metadata.json()
        return self._metadata

    def _get_val(self, name, current_val=None):
        """Handles logic for simple properties."""
        if not self.client.autofetch:
            return current_val
        if name in self._accessed or self._state is None:  # current_val is None
            self.fetch()  # Refresh everything
        self._accessed.add(name)
        return getattr(self, f"_{name}")

    def _get_complex_val(self, name, current_val=None):
        """Handles logic for data/metadata."""
        if not self.client.autofetch:
            return current_val
        if name in self._accessed:
            self.fetch()  # Re-request base
        if getattr(self, f"_{name}") is None:  # fetch sets _meta/data to None
            getattr(self, f"fetch_{name}")()
        self._accessed.add(name)
        return getattr(self, f"_{name}")
