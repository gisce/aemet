# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet import Aemet
import tarfile
from six import PY2
if PY2:
    from cStringIO import StringIO as BytesIO
else:
    from io import BytesIO
import json


class Observations(Aemet):
    def __init__(self, api_key, autofetch=False):
        super(Observations, self).__init__(api_key=api_key, autofetch=autofetch)
        self._idema = None
        self._message_type = None

    def clear(self):
        self.idema(None)
        return self

    def _to_json(self, request):
        result = {}
        if self._message_type:
            content = request.content
            data_io = BytesIO(content)
            with tarfile.open(fileobj=data_io, mode='r:gz') as tar:
                for member in tar.getmembers():
                    f = tar.extractfile(member)
                    if f:
                        if member.name.endswith('.json'):
                            file_content = f.read()
                            file_content = file_content.decode('ISO-8859-15')
                            result[member.name] = json.loads(file_content)
        else:
            result = request.json()
        return result

    def idema(self, idema_value):
        self._message_type = None
        if self._idema != idema_value:
            self._clear()
        self._idema = idema_value
        return self

    def message(self, type_message):
        self._idema = None
        if self._message_type != type_message:
            self._clear()
        self._message_type = type_message
        return self

    @property
    def endpoint(self):
        if self._idema:
            return "observacion/convencional/datos/estacion/{}".format(self._idema)
        elif self._message_type:
            return "observacion/convencional/mensajes/tipomensaje/{}".format(self._message_type)
        return "observacion/convencional/todas"
