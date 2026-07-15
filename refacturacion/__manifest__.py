{
    'name': "Almacén de refacturación",

    'summary': """
        Almacén de refacturación""",

    'description': """
        Crea entradas/salidas automáticas al almacén de refacturación cuando se crea una nota de crédito y cuando
        se utiliza la acción Refactuación crédito
    """,

    'author': "Jonathan Alfaro",
    'license': 'LGPL-3',
    'version': '19.0.1.0.0',
    # MIGRACIÓN V19: el manifest original solo declaraba 'base'/'account',
    # pero el código usa modelos/campos de 'stock', 'sale', el campo
    # `movimientos_almacen` (definido por account_move_proper) y el campo
    # `sale_id` en account.move (definido por sale_purchase_confirm), además
    # de campos de 'l10n_mx_edi'. Se corrige para reflejar las dependencias
    # reales.
    "depends": ["base", "account", "stock", "sale", "l10n_mx_edi", "account_move_proper", "sale_purchase_confirm"],
    'data': [
        'views/account_move.xml',
    ],
}
