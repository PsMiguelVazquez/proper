# -*- coding: utf-8 -*-
{
    'name': "account_bank_statement_proper",

    'summary': """
        Valida y evita duplicar pagos en estados de cuenta bancarios, además
        de enlazar pagos a facturas y líneas de conciliación.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: se agregan 'l10n_mx_edi' (el onchange usa
    # rel_payment.l10n_mx_edi_payment_method_id, ya presente pero no
    # declarado en 15.0) y 'account_accountant' (necesario para heredar la
    # vista moderna del widget de conciliación bancaria, ver views/views.xml).
    'depends': ['base', 'account', 'l10n_mx_edi', 'account_accountant'],

    'data': [
        'views/views.xml',
    ],
}
