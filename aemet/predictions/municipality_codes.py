# -*- coding: utf-8 -*-
from __future__ import absolute_import
import csv
import os

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diccionario24.csv')
MUNICIPALITIES_CODES = []
with open(filepath, 'r', encoding='utf-8') as csv_file:
    next(csv_file)
    reader = csv.DictReader(csv_file, delimiter=',')
    for row in reader:
        MUNICIPALITIES_CODES.append({
            'codauto': row['CODAUTO'].zfill(2),
            'cpro': row['CPRO'].zfill(2),
            'cmun': row['CMUN'].zfill(3),
            'dc': row['DC'],
            'name': row['NOMBRE']
        })
