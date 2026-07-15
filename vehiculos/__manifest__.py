# -*- coding: utf-8 -*-
{
    'name': "vehiculos",

    'summary': """
        Gestiona vehículos, odómetros, marcas/modelos y su relación con
        entregas y transportes.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    # MIGRACIÓN V19: se agrega 'stock_delivery', de donde viene
    # `carrier_tracking_ref` en stock.picking, usado por este módulo.
    'depends': ['base', 'stock', 'fleet', 'hr', 'sale', 'product', 'mrp', 'stock_delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
        'installable': True,
    'application': True,
    'auto_install': False,
}
