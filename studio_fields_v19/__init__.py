import re

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
#
# IMPORTANTE: a diferencia de `_fix_accounting_menu_parents` (apunta a
# xmlids de `account`/`account_reports`, ya cargados antes de que este
# módulo empiece), esta función depende de acciones creadas por ESTE MISMO
# módulo (`data/` en el manifest). `pre_init_hook` y las migraciones
# `pre-*` corren ANTES de que Odoo cargue los `data` del módulo (ver
# `odoo/modules/loading.py`), así que en ese momento `env.ref(...)` todavía
# no encuentra la acción y la función no hace nada silenciosamente. Por
# eso va en `post_init_hook`/una migración `post-*`, que corren después.
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


# MIGRACIÓN V19: campos de Odoo Studio sin ningún uso detectado -no
# aparecen en ninguna vista, en el `related`/`depends`/`compute` de ningún
# otro campo, en el dominio/contexto de ninguna acción/regla/filtro/
# automatización, ni en ninguna plantilla de correo- y con nombre técnico
# nunca personalizado por el usuario (`x_studio_related_field_XXXXX` =
# "New Campo relacionado", `x_studio_char_field_XXXXX` = "New Texto",
# etc.): quedaron abandonados al crearlos con Odoo Studio y nunca se
# terminaron de configurar. `ir.model.fields` no tiene un campo `active`
# en 19.0 (no existe forma de "desactivarlos" sin borrarlos), así que la
# única manera de que Odoo deje de considerarlos es eliminarlos. Se hace
# por código (no por `<record>` con `noupdate`) para que corra también en
# upgrade sobre la base de producción real, donde estos campos siguen
# existiendo como datos de Studio.
UNUSED_STUDIO_FIELDS = [
    ('purchase.order', 'x_id_wizard'),
    ('stock.picking', 'x_studio_binary_field_U2SJO'),
    ('hr.employee', 'x_studio_char_field_3jYFV'),
    ('hr.employee', 'x_studio_char_field_Shl3z'),
    ('stock.picking', 'x_studio_contacto'),
    ('purchase.order', 'x_studio_contacto_del_proveedor_2'),
    ('purchase.order', 'x_studio_date_field_ot4PB'),
    ('stock.picking', 'x_studio_estadodefacturacion'),
    ('hr.expense', 'x_studio_many2many_field_BPqnG'),
    ('crm.lead', 'x_studio_many2many_field_TEfWq'),
    ('purchase.order', 'x_studio_many2many_field_g3klO'),
    ('helpdesk.ticket', 'x_studio_many2one_field_LSlgL'),
    ('stock.move.line', 'x_studio_many2one_field_TDCoI'),
    ('stock.picking', 'x_studio_many2one_field_VbVzT'),
    ('crm.lead', 'x_studio_many2one_field_gXydV'),
    ('stock.picking', 'x_studio_many2one_field_oVjTr'),
    ('sale.order', 'x_studio_many2one_field_u4jVV'),
    ('sale.order.line', 'x_studio_one2many_field_9IYYS'),
    ('stock.warehouse.orderpoint', 'x_studio_one2many_field_nONnm'),
    ('purchase.order', 'x_studio_related_field_1S2Hw'),
    ('stock.picking', 'x_studio_related_field_1zowW'),
    ('stock.picking', 'x_studio_related_field_4dnKs'),
    ('purchase.order', 'x_studio_related_field_7qHNz'),
    ('stock.quant', 'x_studio_related_field_8lPbT'),
    ('sale.order', 'x_studio_related_field_Bxpio'),
    ('stock.picking', 'x_studio_related_field_D32We'),
    ('stock.move.line', 'x_studio_related_field_DX5P3'),
    ('stock.picking', 'x_studio_related_field_DlNTt'),
    ('crm.lead', 'x_studio_related_field_HCLHF'),
    ('sale.order', 'x_studio_related_field_ILzQo'),
    ('stock.move.line', 'x_studio_related_field_IiDLu'),
    ('stock.picking', 'x_studio_related_field_IiiYX'),
    ('stock.picking', 'x_studio_related_field_JrAgC'),
    ('helpdesk.ticket', 'x_studio_related_field_KauYZ'),
    ('stock.move', 'x_studio_related_field_MKUoB'),
    ('stock.move.line', 'x_studio_related_field_MMOYs'),
    ('res.groups', 'x_studio_related_field_MeJGg'),
    ('stock.quant', 'x_studio_related_field_O9PXe'),
    ('stock.move.line', 'x_studio_related_field_OLM4N'),
    ('stock.picking', 'x_studio_related_field_PXVOp'),
    ('stock.move.line', 'x_studio_related_field_PZviD'),
    ('creacion.ruta', 'x_studio_related_field_Qfchv'),
    ('stock.picking', 'x_studio_related_field_RWdrp'),
    ('stock.picking', 'x_studio_related_field_S4pt4'),
    ('stock.move.line', 'x_studio_related_field_SJWVK'),
    ('purchase.order', 'x_studio_related_field_SPaH7'),
    ('sale.order', 'x_studio_related_field_ToH0i'),
    ('stock.picking', 'x_studio_related_field_UHlS7'),
    ('stock.picking', 'x_studio_related_field_UZld3'),
    ('stock.move.line', 'x_studio_related_field_VYaJF'),
    ('helpdesk.ticket', 'x_studio_related_field_VgrKI'),
    ('stock.picking', 'x_studio_related_field_W8qAb'),
    ('stock.move.line', 'x_studio_related_field_WLrvY'),
    ('stock.move', 'x_studio_related_field_Yzeyb'),
    ('stock.picking', 'x_studio_related_field_aI3jO'),
    ('stock.picking', 'x_studio_related_field_cAdjn'),
    ('stock.move.line', 'x_studio_related_field_cxLmz'),
    ('purchase.order', 'x_studio_related_field_eWEyV'),
    ('stock.move.line', 'x_studio_related_field_enbMq'),
    ('stock.picking', 'x_studio_related_field_ep4lV'),
    ('stock.move.line', 'x_studio_related_field_gEKBp'),
    ('stock.move.line', 'x_studio_related_field_jDRZO'),
    ('stock.picking', 'x_studio_related_field_kEXg3'),
    ('stock.picking', 'x_studio_related_field_keuaH'),
    ('stock.picking', 'x_studio_related_field_ldNfa'),
    ('helpdesk.ticket', 'x_studio_related_field_n7DfB'),
    ('stock.picking', 'x_studio_related_field_njrg1'),
    ('stock.move.line', 'x_studio_related_field_nnb1r'),
    ('stock.quant', 'x_studio_related_field_oBnIu'),
    ('sale.order.line', 'x_studio_related_field_oQUFO'),
    ('stock.picking', 'x_studio_related_field_oUiuh'),
    ('stock.picking', 'x_studio_related_field_pYlrY'),
    ('purchase.order', 'x_studio_related_field_pZzGA'),
    ('creacion.ruta', 'x_studio_related_field_ppn8E'),
    ('helpdesk.ticket', 'x_studio_related_field_qXj6L'),
    ('stock.move.line', 'x_studio_related_field_qZMtF'),
    ('stock.picking', 'x_studio_related_field_qwt7c'),
    ('hr.employee', 'x_studio_related_field_sPacb'),
    ('stock.move.line', 'x_studio_related_field_u9fb1'),
    ('stock.move.line', 'x_studio_related_field_uCpSv'),
    ('stock.move', 'x_studio_related_field_wORzK'),
    ('stock.picking', 'x_studio_related_field_wrqJD'),
    ('stock.move.line', 'x_studio_related_field_x8MVw'),
    ('stock.move.line', 'x_studio_related_field_xKS6Y'),
    ('stock.move.line', 'x_studio_related_field_xRYH1'),
    ('stock.picking', 'x_studio_related_field_zAbcR'),
    ('sale.order', 'x_studio_selection_field_hBVNg'),
    ('purchase.order', 'x_studio_text_field_uiFIR'),
]


def _cleanup_unused_studio_fields(env):
    IrModelFields = env['ir.model.fields']
    for model, name in UNUSED_STUDIO_FIELDS:
        field = IrModelFields.search([('model', '=', model), ('name', '=', name), ('state', '=', 'manual')])
        if field:
            field.unlink()


# MIGRACIÓN V19: `l10n_mx_edi` reescribió por completo el manejo de CFDI
# entre v15 y v19 (pasó de métodos/campos sueltos en `account.move` a un
# modelo dedicado `l10n_mx_edi.document`). Cualquier reporte de Studio
# (facturas, remisiones, recibos de pago, entregas con carta porte) que use
# la sintaxis vieja rompe con `AttributeError`/`KeyError` al imprimirse.
# Encontrado y confirmado en pruebas locales -renderizando una copia
# corregida contra una factura real- que estos 4 patrones cubren todos los
# casos presentes en las vistas heredadas de v15:
#   - `X._l10n_mx_edi_decode_cfdi()` -> ya no existe en `account.move`; el
#     reemplazo es `env['l10n_mx_edi.document']._decode_cfdi_attachment(...)`
#     sobre el adjunto firmado.
#   - `bool(X._get_l10n_mx_edi_signed_edi_document())` -> ya no existe; el
#     estado de firma ahora se lee directo del campo `l10n_mx_edi_cfdi_state`.
#   - `X.l10n_mx_edi_cfdi_request in (...)`/`== '...'` -> ese campo
#     (workflow de "solicitud" de CFDI) ya no existe; se reduce a `True`
#     para dejar la condición sólo en manos de `is_cfdi_signed`, que ya
#     acompaña a esta comparación en todos los casos encontrados.
#   - `X.l10n_mx_edi_origin` -> se renombró a `X.l10n_mx_edi_cfdi_origin`.
# Los 3 primeros patrones aplican igual para `account.move`, `account.payment`
# y `stock.picking` (misma API en los 3 módulos de `l10n_mx_edi*`), así que
# el mismo reemplazo sirve para reportes de factura, pago y entrega/carta
# porte por igual.
_L10N_MX_EDI_DECODE_CFDI_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_.]*)\._l10n_mx_edi_decode_cfdi\(\)')
_L10N_MX_EDI_SIGNED_DOC_RE = re.compile(r'bool\(([a-zA-Z_][a-zA-Z0-9_.]*)\._get_l10n_mx_edi_signed_edi_document\(\)\)')
_L10N_MX_EDI_CFDI_REQUEST_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_.]*\.l10n_mx_edi_cfdi_request\s*(?:in\s*\([^)]*\)|==\s*'[^']*')")


def _fix_broken_l10n_mx_edi_reports(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|', '|',
        ('arch_db', 'like', '_l10n_mx_edi_decode_cfdi'),
        ('arch_db', 'like', '_get_l10n_mx_edi_signed_edi_document'),
        ('arch_db', 'like', 'l10n_mx_edi_origin'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _L10N_MX_EDI_DECODE_CFDI_RE.sub(
            lambda m: (
                f"{m.group(1)}.env['l10n_mx_edi.document']._decode_cfdi_attachment("
                f"{m.group(1)}.l10n_mx_edi_cfdi_attachment_id.raw)"
            ),
            arch,
        )
        new_arch = _L10N_MX_EDI_SIGNED_DOC_RE.sub(
            lambda m: f"({m.group(1)}.l10n_mx_edi_cfdi_state in ('sent', 'global_sent'))",
            new_arch,
        )
        new_arch = _L10N_MX_EDI_CFDI_REQUEST_RE.sub('True', new_arch)
        new_arch = new_arch.replace('l10n_mx_edi_origin', 'l10n_mx_edi_cfdi_origin')
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: bug preexistente en las plantillas de Studio (ya estaba
# roto en v15, no es algo que haya cambiado en la migración): usan
# `o.x_num_pro` -"Num Pro"- directo sobre la factura (`account.move`), pero
# ese campo sólo existe en el cliente (`res.partner`, ver
# `res_partner_fields/models/models.py`). En v15 esto no lanzaba error
# porque los campos Studio evaluaban `getattr(o, 'x_num_pro', False)` -sin
# fallar si no existe-; en v19, con el campo ya formalizado como código en
# `res.partner`, `t-field` sobre un modelo que no lo tiene sí revienta con
# `KeyError`. El único uso encontrado en todas las plantillas afectadas es
# como valor a mostrar en el reporte, así que se corrige el camino
# (`o.partner_id.x_num_pro`, el número de cliente real) en vez de solo
# esconder el error.
def _fix_broken_studio_report_field_refs(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', 'o.x_num_pro'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace('o.x_num_pro', 'o.partner_id.x_num_pro')
        if new_arch != arch:
            view.write({'arch_db': new_arch})


def pre_init_hook(env):
    _deactivate_old_studio_report_views(env)
    _fix_accounting_menu_parents(env)
    _cleanup_unused_studio_fields(env)
    _fix_broken_l10n_mx_edi_reports(env)
    _fix_broken_studio_report_field_refs(env)


def post_init_hook(env):
    _fix_sale_order_menu_actions(env)
