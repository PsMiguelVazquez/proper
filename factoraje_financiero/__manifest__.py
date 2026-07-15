# -*- coding: utf-8 -*-
{
    'name': "Factoraje financiero",

    'summary': """
        Factoraje financiero""",

    'description': """
        Aplicación de pagos por Factoraje , ( incluye aplicación de los Interéses correspondientes )
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: `porcent_assign` (account.move) es de `add_invoice_to_paid`
    # (Lote 3); `endoso.move` es de `endoso_proper`; el contexto
    # `paid_amount` en `_reconcile_payments` lo interpreta el
    # `_prepare_reconciliation_single_partial` de `account_payment_widget_amount`
    # (Lote 1). Instalación+pruebas quedan diferidas hasta que
    # `add_invoice_to_paid` esté migrado.
    'depends': ['base', 'account', 'l10n_mx_edi', 'endoso_proper', 'account_payment_widget_amount', 'add_invoice_to_paid'],

    'data': [
        'views/account_move.xml',
        'wizard/factoraje_wizard_view.xml',
        'wizard/compensate_wizard_view.xml',
        'security/ir.model.access.csv',
        'views/account_payment.xml',
    ],
}
