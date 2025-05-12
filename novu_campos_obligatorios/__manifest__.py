# -*- coding: utf-8 -*-
{
    'name': "Novu Campos Obligatorios",

    'summary': """
        Campos obligatorios""",

    'description': """
        Condiciona en varios modulos varios campos que son obligatorios
    """,
    'license': 'LGPL-3',

    'author': "Mayra Carrillo",
    #'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'sale','account','contacts','stock'],

    # always loaded
    'data': [
        #'views/stock_move_view.xml'
        
    ],
}
