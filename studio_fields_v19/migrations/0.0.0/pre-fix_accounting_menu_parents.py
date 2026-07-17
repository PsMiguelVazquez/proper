# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_accounting_menu_parents` en
`__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo para
el detalle de por qué hace falta un `write()` por código en vez de un
`<record>` en un XML de datos (los 6 menús ya tienen `noupdate=True`,
puesto por Studio).
"""
from odoo import api, SUPERUSER_ID

ACCOUNTING_MENU_PARENTS = {
    'account.menu_action_move_journal_line_form': 'account.account_transactions_menu',
    'account.menu_action_account_moves_all': 'account.account_audit_control_menu',
    'account_reports.menu_action_account_report_partner_ledger': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_aged_receivable': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_aged_payable': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_coa': 'account_reports.account_reports_audit_menu',
}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for menu_xmlid, parent_xmlid in ACCOUNTING_MENU_PARENTS.items():
        menu = env.ref(menu_xmlid, raise_if_not_found=False)
        parent = env.ref(parent_xmlid, raise_if_not_found=False)
        if menu and parent and menu.parent_id != parent:
            menu.write({'parent_id': parent.id})
