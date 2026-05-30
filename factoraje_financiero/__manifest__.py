# -*- coding: utf-8 -*-
{
    'name': "Factoraje financiero",

    'summary': """
        Factoraje financiero""",

    'description': """
        Aplicación de pagos por Factoraje , ( incluye aplicación de los Interéses correspondientes )
    """,

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
        'views/account_move.xml',
        'wizard/factoraje_wizard_view.xml',
        'wizard/compensate_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/cfdi4/pago.xml',
        'views/account_payment.xml',
    ],
}
