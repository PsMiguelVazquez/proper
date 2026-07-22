# -*- coding: utf-8 -*-
{
    'name': "Eliminacion de saldos menores",

    'summary':  """
                    Utilidad para eliminación de saldos menores.
                """,

    'description': """
        Genera una acción configurable para eliminar los saldos menores de las cuentas por pagar/cobrar
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.1',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: el manifest original solo declaraba 'base'/'account',
    # pero `payment.amount_rest` lo define el módulo `add_invoice_to_paid`
    # (dependencia real no declarada).
    'depends': ['base', 'account', 'add_invoice_to_paid'],

    'data': [
        'views/account_move.xml',
        'wizard/wizard_eliminate_balance_view.xml',
        'security/ir.model.access.csv',
    ],
}
