# -*- coding: utf-8 -*-
from mamba import describe, context, description, before, it
from expects import expect, equal, be_within, be_true, be_false, start_with
import os
from aemet import Aemet

with description("Testing"):
    with before.all:
        self.api_key = os.getenv('AEMET_TOKEN')

    with describe('Aemet'):
        with context("Observations without autofetch:"):
            with before.all:
                self.aemet = Aemet(api_key=self.api_key, autofetch=False)

            with it('tests the url'):
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/todas'))

            with it('tests the base url'):
                expect(self.aemet.observations.base_url).to(equal('https://opendata.aemet.es/opendata/api/'))

            with it('tests the endpoint'):
                expect(self.aemet.observations.endpoint).to(equal('observacion/convencional/todas'))

            with it('tests the url'):
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/todas'))

            with it('tests the state before calling fetch'):
                expect(self.aemet.observations.state).to(equal(None))

            with it('tests the description before calling fetch'):
                expect(self.aemet.observations.description).to(equal(None))

            with it('tests the response_headers before calling fetch'):
                expect(self.aemet.observations.response_headers).to(equal(None))

            with it('tests the metadata_url before calling fetch'):
                expect(self.aemet.observations.metadata_url).to(equal(None))

            with it('tests the data_url before calling fetch'):
                expect(self.aemet.observations.data_url).to(equal(None))

            with it('tests the metadata before calling fetch'):
                expect(self.aemet.observations.metadata).to(equal(None))

            with it('tests the data before calling fetch'):
                expect(self.aemet.observations.data).to(equal(None))

            with it('tests the fetch'):
                self.aemet.observations.fetch()

            with it('tests the state after calling fetch'):
                expect(self.aemet.observations.state).to(equal(200))

            with it('tests the description after calling fetch'):
                expect(self.aemet.observations.description).to(equal('exito'))

            with it('tests the response_headers after calling fetch'):
                r = self.aemet.observations.response_headers
                remaining_count = r['Remaining-request-count']
                content_type = r['content-type']
                expect(int(remaining_count)).to(be_within(100, 150))
                expect(content_type).to(equal('application/json;charset=ISO-8859-15'))

            with it('tests the metadata_url after calling fetch'):
                expect(self.aemet.observations.metadata_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))

            with it('tests the data_url after calling fetch'):
                expect(self.aemet.observations.data_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))

            with it('tests the metadata after calling fetch'):
                expect(self.aemet.observations.metadata).to(equal(None))
                self.aemet.observations.fetch_metadata()
                metadata = self.aemet.observations.metadata
                res = list(metadata.keys()) == ['unidad_generadora', 'periodicidad', 'formato', 'copyright', 'notaLegal', 'campos']
                expect(res).to(be_true)

            with it('tests the data after calling fetch'):
                expect(self.aemet.observations.data).to(equal(None))
                self.aemet.observations.fetch_data()
                data = self.aemet.observations.data
                res = (isinstance(data, list) and len(data) > 0 and all(isinstance(x, dict) for x in data))
                expect(res).to(be_true)

            with it('tests repeated calls to state'):
                state = self.aemet.observations.state
                expect(id(state)).to(equal(id(self.aemet.observations.state)))

            with it('tests repeated calls to description'):
                description = self.aemet.observations.description
                expect(id(description)).to(equal(id(self.aemet.observations.description)))

            with it('tests repetaed calls to response_headers'):
                r = self.aemet.observations.response_headers
                expect(id(r)).to(equal(id(self.aemet.observations.response_headers)))

            with it('tests repetaed calls to metadata_url'):
                r = self.aemet.observations.metadata_url
                expect(id(r)).to(equal(id(self.aemet.observations.metadata_url)))

            with it('tests repetaed calls to data_url'):
                r = self.aemet.observations.data_url
                expect(id(r)).to(equal(id(self.aemet.observations.data_url)))

            with it('tests repeated calls to metadata'):
                self.aemet.observations.fetch_metadata()
                r = self.aemet.observations.metadata
                expect(id(r)).to(equal(id(self.aemet.observations.metadata)))

            with it('tests repeated calls to data'):
                self.aemet.observations.fetch_data()
                r = self.aemet.observations.data
                expect(id(r)).to(equal(id(self.aemet.observations.data)))

            with it('tests refetching'):
                data_url = self.aemet.observations.data_url
                description = self.aemet.observations.description
                self.aemet.observations.fetch()
                expect(id(data_url)).to_not(equal(id(self.aemet.observations.data_url)))
                expect(id(description)).to_not(equal(id(self.aemet.observations.description)))
                expect(self.aemet.observations.data).to(equal(None))
                expect(self.aemet.observations.metadata).to(equal(None))

            with it('tests fetching an idema'):
                self.aemet.observations.idema('0009X')
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/0009X'))
                expect(self.aemet.observations.data_url).to(equal(None))
                self.aemet.observations.fetch()
                expect(self.aemet.observations.data_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))

        with context("Observatoins with autofetch:"):
            with before.all:
                self.aemet = Aemet(api_key=self.api_key, autofetch=True)

            with it('tests the url'):
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/todas'))

            with it('tests the base url'):
                expect(self.aemet.observations.base_url).to(equal('https://opendata.aemet.es/opendata/api/'))

            with it('tests the endpoint'):
                expect(self.aemet.observations.endpoint).to(equal('observacion/convencional/todas'))

            with it('tests the url'):
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/todas'))

            with it('tests the state'):
                expect(self.aemet.observations.state).to(equal(200))

            with it('tests the description'):
                expect(self.aemet.observations.description).to(equal('exito'))

            with it('tests the response_headers'):
                r = self.aemet.observations.response_headers
                remaining_count = r['Remaining-request-count']
                content_type = r['content-type']
                expect(int(remaining_count)).to(be_within(100, 150))
                expect(content_type).to(equal('application/json;charset=ISO-8859-15'))

            with it('tests the metadata_url'):
                expect(self.aemet.observations.metadata_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))

            with it('tests the data_url'):
                expect(self.aemet.observations.data_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))

            with it('tests the metadata'):
                metadata = self.aemet.observations.metadata
                res = list(metadata.keys()) == ['unidad_generadora', 'periodicidad', 'formato', 'copyright', 'notaLegal', 'campos']
                expect(res).to(be_true)

            with it('tests the data'):
                data = self.aemet.observations.data
                res = (isinstance(data, list) and len(data) > 0 and all(isinstance(x, dict) for x in data))
                expect(res).to(be_true)

            with it('tests repeated calls to state'):  # Status 200 triggers caching of the response body.
                state = self.aemet.observations.state
                expect(id(state)).to(equal(id(self.aemet.observations.state)))

            with it('tests repeated calls to description'):
                description = self.aemet.observations.description
                expect(id(description)).to_not(equal(id(self.aemet.observations.description)))

            with it('tests repetaed calls to response_headers'):
                r = self.aemet.observations.response_headers
                expect(id(r)).to_not(equal(id(self.aemet.observations.response_headers)))

            with it('tests repetaed calls to metadata_url'):
                r = self.aemet.observations.metadata_url
                expect(id(r)).to_not(equal(id(self.aemet.observations.metadata_url)))

            with it('tests repetaed calls to data_url'):
                r = self.aemet.observations.data_url
                expect(id(r)).to_not(equal(id(self.aemet.observations.data_url)))

            with it('tests repeated calls to metadata'):
                r = self.aemet.observations.metadata
                expect(id(r)).to_not(equal(id(self.aemet.observations.metadata)))

            with it('tests repeated calls to data'):
                r = self.aemet.observations.data
                expect(id(r)).to_not(equal(id(self.aemet.observations.data)))

            with it('tests refetching different'):
                data_url = self.aemet.observations.data_url
                metadata_url = self.aemet.observations.metadata_url
                metadata_url = self.aemet.observations.metadata_url
                expect(id(data_url)).to_not(equal(id(self.aemet.observations._data_url)))
                expect(self.aemet.observations._data).to(equal(None))
                expect(self.aemet.observations._metadata).to(equal(None))

            with it('tests fetching an idema'):
                self.aemet.observations.idema('0009X')
                expect(self.aemet.observations.url).to(equal('https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/0009X'))
                expect(self.aemet.observations.data_url).to(start_with('https://opendata.aemet.es/opendata/sh/'))