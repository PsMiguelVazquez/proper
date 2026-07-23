# -*- coding:utf-8 -*-
{
    'name': 'Comunicación Tienda en linea V19, con datos 15',
    'version': '19.0.1.0.2',
    'license': 'LGPL-3',
    'pre_init_hook': 'pre_init_hook',
    # MIGRACIÓN V19: `product_unspsc` pasó a ser un módulo Enterprise (en
    # 15.0 era Community); `ws_tienda.py` lee `product.unspsc_code_id`.
    # `product.public.category`/`product.public_categ_ids` son de
    # `website_sale`, dependencia real no declarada en el manifest v15.
    'depends': [
        'openapi',
        'product',
        'crm',
        'product_unspsc',
        'website_sale',
        ],
    'author': 'Novu Central, Mayra Carrillo',
    'category': '',
    'description': 'Abre endpoints de acceso (lectura y escritura) de productos, categorias y leads/oportunidades.',
    'summary': 'Se agregan métodos para la creación y lectura de algunos datos de algunos modelos',
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/crm_lead_views.xml',

    ]
}
