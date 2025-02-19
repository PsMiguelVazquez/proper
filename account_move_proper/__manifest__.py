# -*- coding: utf-8 -*-
{
    'name': "account_move_proper",

    'summary': """
        Permite definir los tipos de cancelación de una factura""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','product','l10n_mx_edi', 'stock'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'wizard/upload_invoice_view.xml',
        ###'views/views.xml'
        #'views/templates.xml',
    ],

}
