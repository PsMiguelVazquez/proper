# -*- coding: utf-8 -*-
{
    'name': "res_partner_fields",

    'summary': """
       Agrega campos al cliente""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner.xml',
        # 'views/templates.xml',
    ],

}
