# -*- coding: utf-8 -*-
# Copyright 2016, 2018 Mapolgroups

{
    "name": "Mapol Quality Checklist ",
    "summary": "Quality Checklist ",
    "version": "12.1",
    "category": "Tools",
    'author' : 'Mapol Business Solution Pvt Ltd',
    'images': ['static/description/icon.png'],

    'website' : 'http://www.mapolbs.com/',
    "description": """
        To check the quality for the product using customized checklist.
    """,
    "license": "LGPL-3",
    "installable": True,
    'application': True,
    'auto_install': False,
    "depends": [
        'base','stock','product','mapol_gate_entry'
    ],
    "data": [
        'security/ir.model.access.csv',
#         'views/checklist_view.xml',
        'views/checklist_catgory_view.xml',
        'views/product_view.xml',
        'views/checklist_main_view.xml',
    ],
}

