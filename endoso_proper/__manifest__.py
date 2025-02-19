# -*- coding: utf-8 -*-
{
    'name': "Endoso Proper",

    'summary': """
        Endoso de facturas""",

    'description': """
        Permite endosar facturas
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','l10n_mx_edi'],

    # always loaded
    'data': [
        #'views/views.xml',
        #'wizard/endoso_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml'
    ],
}
