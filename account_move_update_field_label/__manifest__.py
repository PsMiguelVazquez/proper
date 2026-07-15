# -*- coding: utf-8 -*-
{
    'name': "account_move_update_field_label",

    'summary': """
        Reemplaza el nombre de la etiqueta 'Importe libre de impuestos' por 'Subtotal""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro",
    'website': "",

    'category': 'Accounting',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['base', 'account', 'l10n_mx_edi', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
