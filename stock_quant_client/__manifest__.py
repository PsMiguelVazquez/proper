# -*- coding: utf-8 -*-
{
    'name': "stock_quant_client",

    'summary': """
        Permite seleccionar un cliente y cambiar los precios en base a su nivel de cliente""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro, Javier Monroy",
    'website': "",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['base', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/change_client_view.xml',
        'views/views.xml'
        #'views/templates.xml',
    ],

}
