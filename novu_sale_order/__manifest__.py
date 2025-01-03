# -*- coding: utf-8 -*-
{
    'name': 'Novu Sale Order',
    'author': 'Mayra',
    'website': '',
    'license': 'LGPL-3',
    'summary': 'Sale Order ',
    'description': """Se agregan bloqueo de creacion de productos en la cotizacion y la orden de venta""",

    'depends': [
        'sale',
    ],
    'assets': {
        
    },
    "data": [
            'views/sale_order_view.xml',
            'security/novu_groups.xml'
    ],
    'demo': [],
    'external_dependencies': {
    },
    'application': True,
    'installable': True,
    'auto_install': True
}
