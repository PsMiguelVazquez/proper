# -*- coding: utf-8 -*-
{
    'name': "Consolidación de órdenes de compra",

    'summary': """
        Consolida las órdenes de compra seleccionadas, cambiando el estado de las ordenes
        consolidadas a consolidado
        """,

    'description': """
        Permite consolidar órdenes de compra
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        'views/views.xml',
        #'wizard/consolidacion_compras_view.xml',
        'security/ir.model.access.csv'
    ],
}
