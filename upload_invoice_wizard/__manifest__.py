# -*- coding: utf-8 -*-
{
    'name': "upload_invoice_sales",

    'summary': """
        Permite subir una adjuntos y asignarla a ordenes de venta""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    'website': "",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',

    # MIGRACIÓN V19: se agrega `sale_purchase_confirm` porque la vista del
    # asistente usa `x_descripcion_corta` (sale.order.line, formalizado ahí).
    'depends': ['base', 'stock', 'sale', 'account', 'purchase', 'l10n_mx_edi', 'sale_purchase_confirm'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/upload_invoice_view.xml',
        'views/views.xml',
    ],
}
