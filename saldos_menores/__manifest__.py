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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/account_move.xml',
        'wizard/wizard_eliminate_balance_view.xml',
        'security/ir.model.access.csv',
    ],
}
