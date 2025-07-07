# -*- coding: utf-8 -*-
{
    'name': "Novu Stock Picking",
    'version': '0.1',
    'depends': ['base','stock'],
    'author': "Mayra Carrillo",
    'category': '',
    'description': """
     Modulo desarrollado para agregar funciones extra al modelo stock picking.
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_usuario_valido_traslado.xml',
        'views/stock_picking.xml',
        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application' :True,
}
