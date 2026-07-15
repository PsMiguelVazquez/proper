# -*- coding: utf-8 -*-
{
    'name': "Heldesk Partner Fields",

    'summary': """""",

    'description': """
    Agrega alguno campos a helpdesk
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: el manifest original solo declaraba 'helpdesk', pero
    # `sale_order_id` lo agrega 'helpdesk_sale' y `picking_ids` lo agrega
    # 'helpdesk_stock' (dependencias reales no declaradas).
    'depends': ['base', 'contacts', 'helpdesk', 'helpdesk_sale', 'helpdesk_stock', 'stock'],

    'data': [
        #'security/ir.model.access.csv',
        #'views/views.xml',

    ],
    'demo': [

    ],
}
