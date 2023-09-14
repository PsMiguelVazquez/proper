# -*- coding: utf-8 -*-
{
    'name': "Utilidades para la orden de venta",

    'summary':  """
                    Utilidades para las órdenes de venta.
                """,

    'description': """
        Algunas utilidades para las órdenes de venta, algunas son:
        - Bloqueo de las líneas de las órdenes de venta cuando están en estado sale.
        - Bloqueo de la facturación si es una orden surtida parcialmente.
        - Solucitud de desbloqueo de la facturación cuando la orden está surtida parcialmente
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase','product','sale_purchase_confirm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/data_validate.xml',
        # 'wizard/sale_purchase_order_alerta.xml',
    ],
}
