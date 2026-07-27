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
    'version': '19.0.1.0.55',
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
        # MIGRACIÓN V19: `x_studio_cant_prod_pedido` (account.move) usa
        # `related='sale_id.cart_quantity'`; `cart_quantity` es un campo de
        # `website_sale` (`addons/website_sale/models/sale_order.py`), no de
        # `sale` ni `website`. Sin esta dependencia explícita, una
        # instalación donde el grafo de módulos no arrastre `website_sale`
        # por otro lado (p. ej. una base de pruebas nueva) falla con
        # "KeyError: Field cart_quantity referenced in related field
        # definition account.move.x_studio_cant_prod_pedido does not
        # exist" al montar el registro.
        'website_sale',
        'helpdesk',
        # MIGRACIÓN V19: `x_studio_fecha_de_surtido_1` (helpdesk.ticket) usa
        # `related='sale_order_id...'`; `sale_order_id` lo agrega
        # `helpdesk_sale` (`enterprise/helpdesk_sale/models/
        # helpdesk_ticket.py`), no `helpdesk` por sí solo. Mismo problema
        # que `website_sale` arriba: sin esta dependencia explícita, una
        # instalación donde nada más arrastre `helpdesk_sale` falla con
        # "KeyError: Field sale_order_id ... does not exist" al montar el
        # registro.
        'helpdesk_sale',
        'hr',
        # MIGRACIÓN V19: `account.payment.x_pagos_extracto` depende
        # (`@api.depends('line_ids.rel_payment')`) de `account.bank.
        # statement.line.rel_payment`, formalizado en
        # `account_bank_statement_proper`; y ese mismo `rel_payment`
        # también existe en `account.move` (formalizado en
        # `factoraje_financiero`), usado por `account.payment.rel_payment`
        # (`related='move_id.rel_payment'` en este mismo archivo). Sin
        # estas dos dependencias explícitas, una instalación donde nada
        # más las arrastre falla con "Dependency field 'rel_payment' not
        # found in model account.bank.statement.line" al montar el
        # registro.
        'account_bank_statement_proper',
        'factoraje_financiero',
        # MIGRACIÓN V19: la vista formalizada de `account.move.form` (ver
        # `views/account_move_form.xml`) usa el botón `button_cancel_posted_
        # moves` y el campo `l10n_mx_edi_cancel_invoice_id`, ambos de
        # `account_edi`, y el botón `action_view_landed_costs` de
        # `stock_landed_costs`. Ninguno de los dos era dependencia de
        # ningún módulo `proper` -aunque sí estaban instalados en la base
        # real de producción, de donde viene la personalización original de
        # Studio-, así que sin declararlos aquí una instalación limpia
        # fallaría con "Element ... cannot be located in parent view".
        'account_edi',
        'stock_landed_costs',
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
        'views/account_move_form.xml',
    ],
}
