# -*- coding: utf-8 -*-
{
    'name': "Bloqueo de órdenes",

    'summary':  """
                    Bloquea las órdenes de venta cuando ya le ha llegado la solicitud de compra de productos a Compras
                """,

    'description': """
        Bloquea las órdenes de venta cuando ya le ha llegado la solicitud de compra de productos a Compras.
    """,
    'license': 'LGPL-3',

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.1',

    # MIGRACIÓN V19: `es_orden_parcial` es un campo real definido por
    # `sale_purchase_confirm` (Lote 3), no declarado en el manifest
    # original de v15.
    'depends': ['base', 'account', 'account_payment_widget_amount', 'l10n_mx_edi', 'sale_purchase_confirm'],

    'data': [
        'views/sale_order.xml',
    ],
}
