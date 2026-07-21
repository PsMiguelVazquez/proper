# -*- coding: utf-8 -*-
{
    'name': "Consolidación de órdenes de compra",

    'summary': """
        Consolida las órdenes de compra seleccionadas, cambiando el estado de las ordenes
        consolidadas a consolidado
        """,

    'description': """
        Permite consolidar órdenes de compra
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.1',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: el manifest original solo declaraba 'base'/'purchase',
    # pero `purchase.order.sale_ids` lo define el módulo
    # `sale_purchase_confirm` (dependencia real no declarada).
    'depends': ['base', 'purchase', 'sale_purchase_confirm'],

    'data': [
        'views/views.xml',
        'wizard/consolidacion_compras_view.xml',
        'security/ir.model.access.csv'
    ],
}
