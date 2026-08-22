# -*- coding: utf-8 -*-
{
    'name': "Endoso Proper",

    'summary': """
        Endoso de facturas""",

    'description': """
        Permite endosar facturas
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.6',
    'pre_init_hook': 'pre_init_hook',

    # MIGRACIÓN V19: `account_move_proper` (campos `x_studio_almacn`,
    # `x_studio_n_orden_de_compra`, `x_referencia`, ahora formalizados como
    # código real) es dependencia real usada en Python por este módulo, no
    # declarada en el manifest original de v15. La instalación de este
    # módulo queda diferida hasta que `account_move_proper` esté disponible
    # (a su vez depende de `sale_purchase_confirm`, Lote 3).
    # NOTA: `add_invoice_to_paid` (dueño de `porcent_assign`) NO se declara
    # aquí a propósito: ese módulo depende de `endoso.move` (definido en
    # este módulo) para su propia lógica, así que declarar la dependencia
    # inversa crearía un ciclo. El uso de `porcent_assign` se mantiene
    # defensivo (ver `models/endoso.py`).
    'depends': ['base', 'account', 'l10n_mx_edi', 'account_move_proper'],

    'data': [
        'views/views.xml',
        'wizard/endoso_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml'
    ],
}
