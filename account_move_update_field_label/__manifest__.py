# -*- coding: utf-8 -*-
{
    'name': "account_move_update_field_label",

    'summary': """
        Reemplaza el nombre de la etiqueta 'Importe libre de impuestos' por 'Subtotal""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    'depends': ['base','account','l10n_mx_edi', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        ##'views/views.xml',
        #'views/templates.xml',
    ],

}
