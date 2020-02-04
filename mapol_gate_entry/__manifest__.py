# -*- coding: utf-8 -*-

{
    "name": "Gate Entry",
    'version': '12.0',
    "author" : "Mapol Business Solutions Pvt Ltd",
    "website": "http://mapolbs-opensource.com",
    'images': ['static/description/icon.png'],
    'summary': "This module provides a gate entry process against the purchase order.",
    'category': 'Gate Entry',
    "depends": [
        "base",
        "purchase",
        "fleet",
        'sale',
        'stock',

    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        "views/inward_entry_view.xml",
        "views/sale_purchase_inward_view.xml",
        'views/outward_entry_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
