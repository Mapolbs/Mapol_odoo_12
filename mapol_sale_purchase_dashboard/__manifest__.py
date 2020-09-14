# -*- coding: utf-8 -*-

{
    "name": "Dashboard for Sale Purchase",
    'version': '12.0.2.0.0',
    "author" : "Mapol Business Solutions Pvt Ltd",
    "website": "http://mapolbs-opensource.com",
    'images': ['static/description/icon.png'],
    'summary': "This module provides a common and customized dashboard which includes sales and purchase details.",
    'category': 'Extra Tools',
    "depends": [
        "base",
        "purchase",
        "sale",
        "stock",
        'custom_purchase',

    ],
    'currency': 'EUR',
    'price': 34.0,
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        "views/dashboard.xml",
        "views/sale_dashboard.xml"
    ],
    'qweb': [
        "static/src/xml/all_dashboard.xml",
        "static/src/xml/sale_dashboard.xml"
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
