# -*- coding: utf-8 -*-
{
    'name': "Bloqueo de órdenes",

    'summary':  """
                    Bloquea las órdenes de venta cuando ya le ha llegado la solicitud de compra de productos a Compras
                """,

    'description': """
        Bloquea las órdenes de venta cuando ya le ha llegado la solicitud de compra de productos a Compras.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_payment_widget_amount', 'l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
}
