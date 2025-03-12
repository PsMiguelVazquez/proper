# -*- coding: utf-8 -*-
{
    'name': 'Novu Trazabilidad por Número de serie y motor',
    'author': 'Mayra Carrillo',
    'website': '',
    'version': '0.1',
    'license': 'LGPL-3',
    'summary': 'Trazabilidad',
    'description': """Se agrega la trazabilidad por numero de motor a la trazabilidad por numero de serie""",

    'depends': ['base', 'stock','sale','account'],
    'assets': {},
    "data": [
        'views/product_template_views.xml',
        'views/stock_move_views.xml',
        'views/stock_quant_views.xml',
        'views/production_lot_views.xml',
        
    ],
    'demo': [],
    'external_dependencies': {},
    'application': False,
    'installable': True,
    'auto_install': False
}
