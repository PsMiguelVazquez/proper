# -*- coding: utf-8 -*-
{
    'name': "Costo promedio proper",

    'summary': """
        Calcula el costo promedio""",

    'description': """
        Calcula el costo promedio de acuerdo a las existencias en los almacenes 0,14,etc. y lo almacena en otro campo
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale_stock', 'stock'],

    # always loaded
    'data': [

    ],
}
