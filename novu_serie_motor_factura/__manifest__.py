# -*- coding: utf-8 -*-
{
    'name': 'Novu Número de serie y motor en factura de venta',
    'author': 'Mayra',
    'website': '',
    'version': '0.1',
    'license': 'LGPL-3',
    'summary': 'Facturacion',
    'description': """Se agregan las vistas para forzar el registro de numero de serie y motor si en las lineas de la factura existe una moto""",

    'depends': ['base', 'account'],
    'assets': {},
    "data": [
            'wizard/wizard_serie_motor_view.xml',
            'security/ir.model.access.csv',
    ],
    'demo': [],
    'external_dependencies': {},
    'application': False,
    'installable': True,
    'auto_install': False
}
