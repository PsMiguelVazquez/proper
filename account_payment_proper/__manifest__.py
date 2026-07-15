# -*- coding: utf-8 -*-
{
    'name': "account_payment_proper",

    'summary': """
        Al crear pagos, genera y adjunta el comprobante de pago PDF al
        asiento relacionado.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['base', 'account'],

    'data': [
        'security/security.xml',
        'views/views.xml',
    ],
}
