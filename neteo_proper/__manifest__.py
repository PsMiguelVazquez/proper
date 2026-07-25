# -*- coding: utf-8 -*-
{
    'name': "Neteo Proper",

    'summary': """
        Pago por compensación""",

    'description': """
        Permite realizar pagos por compensación
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.2',
    'license': 'LGPL-3',
    'pre_init_hook': 'pre_init_hook',

    # MIGRACIÓN V19: la vista del wizard usa `account.move.porcent_assign`,
    # campo real definido por `add_invoice_to_paid` (Lote 3). Instalación y
    # pruebas quedan diferidas hasta que ese módulo esté migrado.
    'depends': ['base', 'account', 'l10n_mx_edi', 'add_invoice_to_paid'],

    'data': [
        'views/views.xml',
        'wizard/neteo_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
}
