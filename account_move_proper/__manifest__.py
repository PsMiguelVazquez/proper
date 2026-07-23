# -*- coding: utf-8 -*-
{
    'name': "account_move_proper",

    'summary': """
        Permite definir los tipos de cancelación de una factura""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jonathan Alfaro",
    'website': "",

    'category': 'Uncategorized',
    'version': '19.0.1.0.8',
    'license': 'LGPL-3',

    'pre_init_hook': 'pre_init_hook',

    # MIGRACIÓN V19: `l10n_mx_edi` pasó a ser un módulo Enterprise (en 15.0
    # era Community); se sirve desde `/home/odoo19/odoo/enterprise`.
    # `account_move_update_field_label` (campo `version_cfdi`),
    # `costo_promedio_proper` (campo `fecha_recepcion_cliente` en
    # `stock.picking`), `upload_invoice_wizard` (`repair_invoice()` usa el
    # modelo/vista `upload.invoice.wizard`), `res_partner_fields` (campos
    # `x_nom_corto_agente_venta`/`x_nombre_corto_tpago`/`x_estado_cli_actua`
    # en `res.partner`, ahora formalizados como código real) y
    # `sale_purchase_confirm` (campo `x_studio_n_orden_de_compra` en
    # `sale.order`) son dependencias reales usadas en Python por este
    # módulo, no declaradas en el manifest original de v15.
    'depends': [
        'base', 'account', 'product', 'l10n_mx_edi', 'stock',
        'account_move_update_field_label', 'costo_promedio_proper',
        'upload_invoice_wizard', 'res_partner_fields', 'sale_purchase_confirm',
        # MIGRACIÓN V19: se agrega para poder usar `edi_state` en el
        # `required=` real de `motivo_cancelacion` (ver comentario en
        # `views/views.xml`); antes no era dependencia de ningún módulo
        # `proper`, así que se simplificaba esa condición.
        'account_edi',
    ],

    'data': [
        'views/views.xml',
    ],
}
