# -*- coding: utf-8 -*-
{
    'name': "stock_quant_client",

    'summary': """
        Permite seleccionar un cliente y cambiar los precios en base a su nivel de cliente""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro, Javier Monroy",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/change_client_view.xml',
        'views/views.xml'
        #'views/templates.xml',
    ],

}
