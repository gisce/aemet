# -*- coding: utf-8 -*-
from __future__ import absolute_import
from aemet.base import Endpoint
import tarfile
from six import PY2
if PY2:
    from cStringIO import StringIO as BytesIO
else:
    from io import BytesIO
import json

from enum import Enum


class MessageType(Enum):
    CLIMAT = "climat"
    SYNOP = "synop"
    TEMP = "temp"
    TODOS = "todos"

    def __str__(self):
        return self.value


class Observations(Endpoint):
    MESSAGE_TYPE = MessageType

    def __init__(self, client):
        super(Observations, self).__init__(client)
        self._idema = None
        self._message_type = None

    def _to_json(self, response):
        result = {}
        if self._message_type:
            content = response.content
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
            result = response.json()
        return result

    def idema(self, idema_value):
        self._message_type = None
        if self._idema != idema_value:
            self._clear()
        self._idema = idema_value
        return self

    def message(self, message_type):
        self._idema = None
        if self._message_type != message_type:
            self._clear()
        self._message_type = message_type
        return self

    @property
    def endpoint(self):
        if self._idema:
            return "observacion/convencional/datos/estacion/{}".format(self._idema)
        elif self._message_type:
            return "observacion/convencional/mensajes/tipomensaje/{}".format(self._message_type)
        return "observacion/convencional/todas"
