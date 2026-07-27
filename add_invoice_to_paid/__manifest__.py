# -*- coding: utf-8 -*-
{
    'name': "add_invoice_to_paid",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.4',

    # MIGRACIÓN V19: `endoso_proper` es dependencia real (usa el modelo
    # `endoso.move`), no declarada en el manifest original de v15.
    'depends': ['base', 'account', 'account_payment_widget_amount', 'l10n_mx_edi', 'endoso_proper'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # MIGRACIÓN V19: la clave `demo` apuntaba a `demo/demo.xml`, un archivo
    # que nunca existió en el módulo (carpeta `demo/` ausente); era una
    # referencia rota ya en 15.0. Se quita en vez de crear datos demo
    # inventados.
}
