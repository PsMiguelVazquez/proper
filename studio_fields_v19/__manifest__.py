# -*- coding: utf-8 -*-
{
    'name': "studio_fields_v19",

    'summary': """
       Formaliza como código los campos calculados creados con Odoo Studio""",

    'description': """
        MIGRACIÓN V19: este módulo reemplaza, con definiciones de campo
        reales en Python, los campos calculados que existían únicamente
        como metadatos de Odoo Studio (ir.model.fields con `compute` en
        texto, evaluado con safe_eval). Studio sigue funcionando en v19,
        pero varios de esos cálculos usaban nombres de campo del core que
        cambiaron en la migración (p.ej. `res.groups.users`,
        `stock.move.reserved_availability`), lo que producía RPC_ERROR al
        abrir los registros. Al pasarlos a código:

        - Se corrigen las referencias a campos renombrados/eliminados.
        - Se corrigen errores latentes encontrados de paso (compute que no
          asignaba valor en todas las ramas, `read_group` con nombre de
          campo incorrecto, dependencias que se referenciaban a sí mismas).
        - Los campos quedan versionados junto con el resto del código.

        No incluye los campos que dependen del subsistema de
        "Requerimientos/Propuestas de compra" (hay dos implementaciones
        paralelas de esos modelos en `sale_purchase_confirm` -
        `x_client_requirement`/`x_proposal_purchase` y
        `requiriment.client`/`proposal.purchases` - y faltan por definir
        los campos relacionales que los conectan con `sale.order`; se deja
        pendiente hasta resolver esa duplicación).
    """,

    'author': "Novu Central",
    'website': "http://www.novucentral.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.23',
    'license': 'LGPL-3',

    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',

    'depends': [
        'sale_purchase_confirm',
        'sale_stock',
        'account',
        'account_reports',
        'purchase',
        'stock',
        'product',
        'crm',
        'l10n_mx_edi_stock',
        'costo_promedio_proper',
        'vehiculos',
        'hr_expense',
        'product_email_template',
        'res_partner_fields',
        'account_payment_proper',
        'website',
        'helpdesk',
        'hr',
    ],

    'data': [
        'views/report_saleorder_document_copy_3.xml',
        'views/report_saleorder_document_copy_3_customization.xml',
        'views/document_tax_totals_copy_1.xml',
        'views/report_saleorder_pro_forma_copy_1.xml',
        'views/report_saleorder_document_copy_3_copy_1.xml',
        'views/document_tax_totals_copy_1_copy_1.xml',
        'views/report_saleorder_pro_forma_copy_1_copy_1.xml',
        'views/stock_picking_form.xml',
        'views/stock_move_line_detailed_operation_tree.xml',
        'views/product_template_form.xml',
        'views/crm_lead_form.xml',
        'views/sale_order_list_cotizaciones.xml',
        'views/sale_order_list_pedidos.xml',
        'views/sale_order_list_marketplace.xml',
        'views/res_partner_form.xml',
    ],
}
