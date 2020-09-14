# -*- coding: utf-8 -*-
# Copyright 2016, 2018 Mapolgroups

{
    "name": "Mapol Custom Purchase",
    "summary": "Production Purchase & General Purchase",
    "version": "12.1",
    "category": "Purchase",
    'author' : 'Mapol Business Solution Pvt Ltd',
    'website' : 'http://www.mapolbs.com/',
    "description": """
        Slipt Purchase into General Purchase and Production Purchase.
    """,
    'currency': 'EUR',
    'price': 0.0,
    "license": "OPL-1",
    "installable": True,
    'application': True,
    'auto_install': False,
    "depends": [
        'base','purchase','product'
    ],
    "data": [
        'view/purchase_view.xml',
    ],
}

