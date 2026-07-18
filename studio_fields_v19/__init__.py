from . import models

# MIGRACIÓN V19: las vistas/reportes formalizados aquí (ver views/) usan a
# propósito el mismo `key`/`t-name` técnico que las vistas originales
# creadas en Odoo Studio, para que cualquier referencia externa (acciones
# de reporte, otros `t-call`) siga apuntando al mismo lugar. Pero eso deja
# a las vistas viejas de Studio (`studio_customization.*`, `state='manual'`)
# convivendo en la base de datos junto a estas nuevas -Odoo no las
# reemplaza automáticamente-, y dependiendo de cuál gane la resolución de
# QWeb, el reporte puede seguir usando el contenido viejo y roto (con los
# nombres de campo de antes de la migración). Este hook desactiva esas
# vistas viejas para que sólo quede activa la versión formalizada aquí.
OLD_STUDIO_VIEW_XMLIDS = [
    'studio_customization.report_saleorder_doc_67c4399c-f382-4d8e-932e-e820104b7fd',
    'studio_customization.odoo_studio_report_s_07964ef2-b734-4ddc-8a9a-88137e048216',
    'studio_customization.document_tax_totals_32e1fed0-21e9-4ea0-8b41-ceb2b094f137',
    'studio_customization.report_saleorder_pro_be1a584c-a8ce-4ab7-944a-7283f77025c0',
    'studio_customization.report_saleorder_pro_19c7eaa3-bc03-42de-9f78-0863b2efaea8',
]

# Además de esos 5 xmlids conocidos, se busca por `key` cualquier otra
# vista de Studio con el mismo nombre técnico que las formalizadas aquí,
# por si hay una que no tengamos identificada por xmlid (p.ej. la de
# "Productos de Muestra" o su plantilla de totales).
OWN_VIEW_KEYS = [
    'sale.report_saleorder_document_copy_3',
    'sale.report_saleorder_document_copy_3_copy_1',
    'account.document_tax_totals_copy_1',
    'account.document_tax_totals_copy_1_copy_1',
    'sale.report_saleorder_pro_forma_copy_1',
    'sale.report_saleorder_pro_forma_copy_1_copy_1',
]


def _deactivate_old_studio_report_views(env):
    IrUiView = env['ir.ui.view']
    to_deactivate = env['ir.ui.view']

    for xmlid in OLD_STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view:
            to_deactivate |= view

    own_views = IrUiView.search([
        ('key', 'in', OWN_VIEW_KEYS),
        ('id', 'not in', to_deactivate.ids or [0]),
    ])
    for view in own_views:
        if not (view.get_external_id().get(view.id, '') or '').startswith('studio_fields_v19.'):
            to_deactivate |= view

    if to_deactivate:
        to_deactivate.write({'active': False})


# MIGRACIÓN V19: estos 6 elementos de menú del core (`account`/
# `account_reports`, no duplicados de Studio -confirmado por su ID
# externo-) tienen `parent_id` vacío en producción, por lo que Odoo los
# muestra como aplicaciones de nivel superior en vez de submenús de
# Contabilidad (probablemente Studio los tocó al reordenar menús en algún
# momento). Studio marca todo lo que toca como `noupdate=True`, así que un
# `<record>` en un XML de datos NO alcanza para corregirlos -Odoo se salta
# la escritura en upgrade cuando el registro destino ya tiene
# `noupdate=True`, sin importar qué módulo la pida (`_load_records` en
# odoo/orm/models.py)-; hay que escribir el campo directo por código.
ACCOUNTING_MENU_PARENTS = {
    'account.menu_action_move_journal_line_form': 'account.account_transactions_menu',
    'account.menu_action_account_moves_all': 'account.account_audit_control_menu',
    'account_reports.menu_action_account_report_partner_ledger': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_aged_receivable': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_aged_payable': 'account.account_reports_partners_reports_menu',
    'account_reports.menu_action_account_report_coa': 'account_reports.account_reports_audit_menu',
}


def _fix_accounting_menu_parents(env):
    for menu_xmlid, parent_xmlid in ACCOUNTING_MENU_PARENTS.items():
        menu = env.ref(menu_xmlid, raise_if_not_found=False)
        parent = env.ref(parent_xmlid, raise_if_not_found=False)
        if menu and parent and menu.parent_id != parent:
            menu.write({'parent_id': parent.id})


# MIGRACIÓN V19: los 3 menús de "Contabilidad/Ventas" (Cotizaciones por
# aprobar, Pedidos de ventas, Marketplace) son acciones+vistas 100% de
# Studio (`studio_customization.*`, sin xmlid la vista de lista). El
# dominio de la acción puede sobrevivir un rebuild, pero la vista de lista
# con las columnas extra (Almacén, Cant. Asignada/Entregada, Estado de
# surtido, etc.) no tiene xmlid -ni siquiera Studio puede reconstruirla
# de forma confiable-, así que se pierde. Se reasigna cada menú (mismos
# xmlids desde antes de la migración) a la acción formalizada aquí. Igual
# que con `ACCOUNTING_MENU_PARENTS`: los menús de Studio quedan
# `noupdate=True`, así que hay que escribir el campo por código.
SALE_ORDER_MENU_ACTIONS = {
    'studio_customization.contabilidad_cotizac_b7903b48-2807-4d8d-8bf6-1949a1d8fc97':
        'studio_fields_v19.sale_order_action_cotizaciones',
    'studio_customization.contabilidad_pedidos_5882ae4a-d4c7-490e-b8c2-0ac2e90862e1':
        'studio_fields_v19.sale_order_action_pedidos',
    'studio_customization.contabilidad_marketp_5f4c41a1-055a-4c7c-8479-64c1082dd7bb':
        'studio_fields_v19.sale_order_action_marketplace',
}


def _fix_sale_order_menu_actions(env):
    for menu_xmlid, action_xmlid in SALE_ORDER_MENU_ACTIONS.items():
        menu = env.ref(menu_xmlid, raise_if_not_found=False)
        action = env.ref(action_xmlid, raise_if_not_found=False)
        if not (menu and action):
            continue
        action_ref = 'ir.actions.act_window,%d' % action.id
        if menu.action != action_ref:
            menu.write({'action': action_ref})


def pre_init_hook(env):
    _deactivate_old_studio_report_views(env)
    _fix_accounting_menu_parents(env)
    _fix_sale_order_menu_actions(env)
