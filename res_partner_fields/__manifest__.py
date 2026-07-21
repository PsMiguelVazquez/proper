# -*- coding: utf-8 -*-
{
    'name': "res_partner_fields",

    'summary': """
       Agrega campos al cliente""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.4',
    'license': 'LGPL-3',

    'depends': ['base', 'l10n_mx_edi'],

    'pre_init_hook': 'pre_init_hook',

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
    ],
}
