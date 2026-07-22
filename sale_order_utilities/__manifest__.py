# -*- coding: utf-8 -*-
{
    'name': "Utilidades para la orden de venta",

    'summary': """
                    Utilidades para las órdenes de venta.
                """,

    'description': """
        Algunas utilidades para las órdenes de venta, algunas son:
        - Bloqueo de las líneas de las órdenes de venta cuando están en estado sale.
        - Bloqueo de la facturación si es una orden surtida parcialmente.
        - Solucitud de desbloqueo de la facturación cuando la orden está surtida parcialmente
    """,

    'license': 'LGPL-3',
    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.5',

    # MIGRACIÓN V19: `data.validate.branch` depende de
    # `product.template.x_studio_rama` -formalizado en `studio_fields_v19`,
    # no en este módulo-; sin esta dependencia declarada, el campo puede no
    # existir todavía cuando este módulo carga (el orden real dependía de
    # que este módulo también declarara su propia copia de `x_studio_rama`,
    # ya eliminada por duplicada, ver `models/sale_order.py`).
    'depends': ['base', 'sale', 'purchase', 'product', 'sale_purchase_confirm', 'studio_fields_v19'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/data_validate.xml',
    ],
}
