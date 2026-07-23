# -*- coding: utf-8 -*-
{
    'name': "sale_purchase_confirm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.17',

    # MIGRACIÓN V19: se agrega `res_partner_fields` (formaliza
    # `x_grupo_cliente`, `x_estado_cli_actua`, `sales_agent`,
    # `x_studio_uso_de_cfdi`, `x_studio_mtodo_de_pago`, `x_nivel_cliente`,
    # `x_nombre_agente_venta`, `x_es_marketplace`, `x_studio_triple_a`,
    # `x_nombre_supervisor_credito` en res.partner) y `l10n_mx_edi` (campos
    # `l10n_mx_edi_usage`/`l10n_mx_edi_payment_method_id`/
    # `l10n_mx_edi_cfdi_origin` en account.move/sale.order), ambos usados
    # directamente por este módulo.
    # `stock_account` se agrega explícitamente porque `x_studio_ultimo_costo`
    # (product.template) usa `stock.valuation.layer`, definido ahí.
    'depends': ['base', 'sale', 'purchase', 'stock', 'stock_account', 'web_studio', 'res_partner_fields', 'l10n_mx_edi'],

    'pre_init_hook': 'pre_init_hook',

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/views_requi.xml',
        'views/product_template_view.xml',
        'views/account_move_view.xml',
    ],
}
