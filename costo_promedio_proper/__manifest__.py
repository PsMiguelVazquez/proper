# -*- coding: utf-8 -*-
{
    'name': "Costo promedio proper",

    'summary': """
        Calcula el costo promedio""",

    'description': """
        Calcula el costo promedio de acuerdo a las existencias en los almacenes 0,14,etc. y lo almacena en otro campo
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: `purchase.order.sale_ids` (usado en `_compute_origin`)
    # es un campo real definido por `sale_purchase_confirm` (Lote 3), no por
    # `sale_stock`/`stock`; se declara como dependencia real. La
    # instalación+pruebas de este módulo quedan diferidas hasta que
    # `sale_purchase_confirm` esté migrado.
    'depends': ['base', 'product', 'sale_stock', 'stock', 'sale_purchase_confirm'],

    'data': [],
}
