# -*- coding: utf-8 -*-
{
    'name': "Consolidación de ventas",

    'summary': """
        Consolida las líneas de la orden de venta para crear una factura""",

    'description': """
        Permite consolidar las líneas de la orden de venta y crear una factura a partir de esta
        en el orden seleccionado en el wizard
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: `res_partner_fields` (x_studio_uso_de_cfdi,
    # x_studio_mtodo_de_pago, x_nombre_corto_tpago), `account_move_proper`
    # (x_referencia, x_studio_orden_de_compra, x_studio_almacn en
    # account.move) y `sale_purchase_confirm` (x_studio_n_orden_de_compra en
    # sale.order) son dependencias reales, ahora que esos campos de Studio
    # se formalizaron como código. Instalación+pruebas quedan diferidas
    # hasta que esos módulos (Lote 3) estén migrados.
    'depends': [
        'base', 'sale', 'account', 'l10n_mx_edi', 'res_partner_fields',
        'account_move_proper', 'sale_purchase_confirm',
    ],

    'data': [
        'views/views.xml',
        'wizard/consolidacion_wizard_view.xml',
        'security/ir.model.access.csv'
    ],
}
