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


# MIGRACIÓN V19: `purchase.order.line.product_uom` se renombró a
# `product_uom_id` (mismo patrón que otros renames del core). La vista de
# Studio "report_purchasequotation_document copy(1) customization" (sin
# xmlid) todavía usa el nombre viejo en dos `t-field`, causando
# `AttributeError: 'purchase.order.line' object has no attribute
# 'product_uom'` al generar el PDF de la cotización de compra.
def _fix_broken_purchase_order_uom_ref(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', 'order_line.product_uom.display_name'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace(
            'order_line.product_uom.display_name',
            'order_line.product_uom_id.display_name',
        )
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: `purchase.order.notes` se renombró a `note` (sin "s").
# Varias vistas de Studio (reportes de cotización/orden de compra y sus
# copias, todas sin xmlid propio -módulo fantasma `studio_customization`,
# `noupdate=True`, nunca se auto-corrigen-) todavía usan el nombre viejo,
# con distintas variables de plantilla (`o.notes`, `doc.notes`,
# `o.related_purchase_id.notes`), causando `KeyError: 'notes'` al generar
# el PDF. Se reemplaza el sufijo `.notes"` por `.note"` sin importar el
# prefijo, ya que el patrón sólo calza cuando "notes" es el último tramo
# del camino de campo (justo antes de la comilla de cierre).
def _fix_broken_purchase_order_notes_ref(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', '.notes"'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace('.notes"', '.note"')
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: causa raíz de "Operación no válida ... no incluye los
# atributos 'data-oe-model' y 'data-oe-id'" en las facturas de Studio
# (Factura Proper, Remisión sin costos, Remisión con Costos, etc.) una vez
# que el CFDI ya está firmado. `account.move._get_name_invoice_report()`
# (`l10n_mx_edi/models/account_move.py`) devuelve
# `'l10n_mx_edi.report_invoice_document'` en vez de
# `'account.report_invoice_document'` cuando la factura ya tiene el CFDI
# firmado -comportamiento nuevo/distinto de v15-. El reporte "envoltorio"
# (`account.report_invoice_with_payments...`) sólo llama a la plantilla de
# contenido si el nombre coincide EXACTO; Odoo lo sabe y por eso
# `l10n_mx_edi/views/report_invoice.xml` parcha (por xpath,
# `inherit_id="account.report_invoice"`) el reporte ORIGINAL agregando un
# `t-elif` para el segundo caso (comentario en el propio código de Odoo:
# "Workaround for Studio reports, see odoo/odoo#60660"). Pero ese parche
# sólo alcanza a la plantilla original -no a los duplicados que crea
# Studio al "copiar" un reporte, que son plantillas 100% independientes,
# sin relación de herencia con el original-, así que para una factura ya
# firmada el `t-if` de estas copias nunca se cumple, no se renderiza nada,
# y Odoo no encuentra ningún `data-oe-id` en el HTML resultante al intentar
# guardarlo como adjunto. Se corrige el `t-if` de cada copia para que
# acepte también el nombre de plantilla de `l10n_mx_edi` (se excluyen
# `account.report_invoice`/`account.report_invoice_with_payments`, los 2
# reportes originales -no duplicados de Studio-, que ya están bien
# resueltos por el parche de Odoo).
_L10N_MX_EDI_INVOICE_REPORT_NAME_RE = re.compile(
    r"_get_name_invoice_report\(\) == 'account\.report_invoice_document'"
)
_CORE_INVOICE_REPORT_KEYS = {'account.report_invoice', 'account.report_invoice_with_payments'}


def _fix_broken_studio_invoice_report_wrappers(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', "_get_name_invoice_report() == 'account.report_invoice_document'"),
    ])
    for view in views:
        if view.key in _CORE_INVOICE_REPORT_KEYS:
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _L10N_MX_EDI_INVOICE_REPORT_NAME_RE.sub(
            "_get_name_invoice_report() in ('account.report_invoice_document', 'l10n_mx_edi.report_invoice_document')",
            arch,
        )
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: `account.move.line.display_type` cambió de significado.
# Antes (v15) una línea de producto normal tenía ese campo vacío/`False`
# -sólo las líneas de sección/nota tenían un valor-, así que Studio (y el
# propio Odoo en ese entonces) usaba `not line.display_type` para decir "es
# una línea contable normal". En v19 TODAS las líneas tienen un valor
# explícito, incluidas las de producto (`'product'`); `not line.display_type`
# ya no es cierto para ninguna línea, así que ese bloque -con toda la fila
# de la tabla: cantidad, producto, precio, etc.- nunca se renderiza y el
# reporte sale con la tabla de líneas vacía. El propio core de Odoo ya
# migró a comparar contra el valor explícito
# (`addons/account/views/report_invoice.xml`: `line.display_type == 'product'`);
# se aplica el mismo cambio a las copias de Studio.
# OJO: esto es específico de `account.move.line` -las líneas de
# `sale.order`/`purchase.order` NO tienen `'product'` como opción de
# `display_type` (sigue siendo `False` para líneas normales, ver
# `addons/sale/models/sale_order_line.py`), así que ahí `not line.display_type`
# sigue siendo la comprobación correcta y no se debe tocar-. Se filtra por
# `invoice_line_ids` (sólo aparece en reportes de factura) para no rozar los
# reportes de cotización/orden de compra que comparten el mismo `.copy_N` de
# Studio pero con `order_line` en vez de `line`.
def _fix_broken_invoice_report_display_type(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', 'not line.display_type'),
        ('arch_db', 'like', 'invoice_line_ids'),
    ])
    for view in views:
        if view.key == 'account.report_invoice_document':
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace('not line.display_type', "line.display_type == 'product'")
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: `tax_totals_json` (v15, un string JSON que había que
# parsear con `json.loads()`) se renombró a `tax_totals` y ahora es
# directamente el diccionario de Python (`addons/account/models/account_move.py`,
# campo `tax_totals`, `compute='_compute_tax_totals'`); ya no hace falta
# `json.loads()`. Afecta tanto a las plantillas QWeb de reportes (factura,
# cotización, orden de compra) como a la vista de formulario Studio
# `sale.order.form.mkp`, que todavía declara `<field name="tax_totals_json">`.
def _fix_broken_tax_totals_json(env):
    IrUiView = env['ir.ui.view']
    views = IrUiView.search([('arch_db', 'like', 'tax_totals_json')])
    external_ids = views.get_external_id()
    for view in views:
        # sólo se toca lo que es de Studio (sin módulo dueño, o dueño
        # `studio_customization`); lo que pertenece a un módulo real
        # (`account`, `sale`, `purchase`, `sale_management`,
        # `account_invoice_extract`, ...) ya trae el campo correcto en su
        # propio código y no debe tocarse aquí.
        xmlid = external_ids.get(view.id) or ''
        owner_module = xmlid.split('.')[0] if '.' in xmlid else ''
        if owner_module and owner_module != 'studio_customization':
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = re.sub(r'json\.loads\(([a-zA-Z_][a-zA-Z0-9_.]*)\.tax_totals_json\)', r'\1.tax_totals', arch)
        new_arch = new_arch.replace('tax_totals_json', 'tax_totals')
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: además del rename `tax_totals_json` -> `tax_totals`
# (`_fix_broken_tax_totals_json`), el propio DICCIONARIO que arma
# `_get_tax_totals_summary()` cambió de forma por completo entre v15 y v19,
# no sólo de nombre:
#   - v15: cada `subtotal`/`amount_by_group` ya traía el importe como texto
#     formateado listo para imprimir (`formatted_amount`,
#     `formatted_tax_group_amount`, etc.), y los grupos de impuestos se
#     buscaban aparte con `tax_totals['groups_by_subtotal'][subtotal_to_show]`.
#   - v19: los importes son números crudos (`base_amount_currency`,
#     `tax_amount_currency`, ...) que hay que formatear en la vista con
#     `t-options="{'widget': 'monetary', ...}"`, y cada `subtotal` ya trae
#     sus propios `tax_groups` anidados (`subtotal['tax_groups']`), sin
#     necesidad de buscarlos aparte.
# Encontrado al probar "Factura Moto" con una línea con impuesto real (con
# una factura sin impuestos el `t-foreach` de grupos queda vacío y el
# `KeyError` no se dispara -así pasó inadvertido en pruebas anteriores con
# facturas de prueba sin impuestos configurados-. Los 4 pares
# `account.document_tax_totals_copy_N`/`account.tax_groups_totals_copy_N`
# de Studio son bit-a-bit idénticos entre sí (sólo cambia el nombre propio y
# la referencia al que llaman), así que se reescriben con la misma lógica
# que usa el core actual (`addons/account/views/report_invoice.xml`,
# `document_tax_totals_template`/`tax_groups_totals_template`) manteniendo
# el estilo visual original de Studio (bordes, `font-size:12px`, etc.).
_TAX_TOTALS_DOCUMENT_TEMPLATE = """<t t-name="account.document_tax_totals_copy_{n}">
            <t t-set="same_tax_base" t-value="tax_totals['same_tax_base']"/>
            <t t-set="currency" t-value="o.currency_id"/>
            <t t-foreach="tax_totals['subtotals']" t-as="subtotal">
                <tr class="border-black o_subtotal">
                    <td style="border-right: black 1px solid;" class="small"><strong t-esc="subtotal['name']"/></td>

                    <td class="text-right small bg-white">
                        <span t-att-class="oe_subtotal_footer_separator" t-out="subtotal['base_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                    </td>
                </tr>

                <t t-call="account.tax_groups_totals_copy_{n}"/>
            </t>

            <!--Total amount with all taxes-->
            <tr class="border-black o_total">
                <td style="font-size:12px; color: black; border-right: black 1px solid;" class="bg-white"><strong style="font-size:12px; color: black;">Total</strong></td>
                <td style="font-size:12px;" class="text-right bg-white">
                    <span style="font-size:12px; color: black;" t-out="tax_totals['total_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                </td>
            </tr>
        </t>"""

_TAX_GROUPS_TEMPLATE = """<t t-name="account.tax_groups_totals_copy_{n}">
            <t t-foreach="subtotal['tax_groups']" t-as="tax_group">
                <tr>
                    <t t-if="same_tax_base or tax_group['display_base_amount_currency'] is False">
                        <td class="small"><span class="text-nowrap" t-esc="tax_group['group_name']"/></td>
                        <td class="text-right o_price_total small bg-white">
                            <span class="text-nowrap" t-out="tax_group['tax_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                        </td>
                    </t>
                    <t t-else="">
                        <td>
                            <span t-esc="tax_group['group_name']"/>
                            <span class="text-nowrap"> on
                                <span t-out="tax_group['display_base_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                            </span>
                        </td>
                        <td class="text-right o_price_total">
                            <span class="text-nowrap" t-out="tax_group['tax_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                        </td>
                    </t>
                </tr>
            </t>
        </t>"""

# MIGRACIÓN V19: `_copy_1` y `_copy_1_copy_1` NO van aquí -ya están
# formalizados correctamente en `views/document_tax_totals_copy_1.xml` y
# `views/document_tax_totals_copy_1_copy_1.xml`, con la lógica de grupos de
# impuestos ya en línea (sin sub-plantilla separada) para los reportes de
# cotización ("Remisión MKP"/"Productos de Muestra"); sobrescribirlos aquí
# perdería esa versión ya validada-. Sólo `_copy_2` y `_copy_3` (usados por
# reportes de FACTURA) seguían con la estructura vieja de Studio.
_TAX_TOTALS_COPY_SUFFIXES = ['2', '3']


def _fix_broken_tax_totals_structure(env):
    IrUiView = env['ir.ui.view']
    for suffix in _TAX_TOTALS_COPY_SUFFIXES:
        doc_view = IrUiView.search([('key', '=', f'account.document_tax_totals_copy_{suffix}')], limit=1)
        if doc_view and doc_view.arch_db != _TAX_TOTALS_DOCUMENT_TEMPLATE.format(n=suffix):
            doc_view.write({'arch_db': _TAX_TOTALS_DOCUMENT_TEMPLATE.format(n=suffix)})
        groups_view = IrUiView.search([('key', '=', f'account.tax_groups_totals_copy_{suffix}')], limit=1)
        if groups_view and groups_view.arch_db != _TAX_GROUPS_TEMPLATE.format(n=suffix):
            groups_view.write({'arch_db': _TAX_GROUPS_TEMPLATE.format(n=suffix)})


# MIGRACIÓN V19: `modifiers="..."` en un `<field>` de vista tree/form es un
# atributo que Odoo SIEMPRE calculó en tiempo de ejecución a partir de
# `invisible=`/`readonly=`/`required=` (o del viejo `attrs=`); nunca debía
# guardarse tal cual en el arch, pero algunas exportaciones de Studio lo
# dejaron grabado literalmente. El validador RelaxNG de v19 es más estricto
# que el de v15 y lo rechaza directo ("Invalid attribute modifiers for
# element field"), lo que además hace que Odoo descarte la vista completa
# como inválida (mensajes en cascada como "Element list has extra content:
# field"/"Expecting an element data, got nothing" para la misma vista).
# Se encontraron sólo 4 variantes de contenido en las 20 vistas afectadas
# (confirmado por inspección directa de cada una): se reemplaza cada una
# por sus atributos reales equivalentes -o se elimina sin más si estaba
# vacío (`{}`, no aportaba nada)-.
_MODIFIERS_REPLACEMENTS = [
    (' modifiers="{}"', ''),
    (' modifiers="{&quot;readonly&quot;: true, &quot;required&quot;: true}"', ' readonly="1" required="1"'),
    (' modifiers="{&quot;readonly&quot;: true}"', ' readonly="1"'),
    (' modifiers="{&quot;required&quot;: true}"', ' required="1"'),
]


def _fix_broken_modifiers_attribute(env):
    views = env['ir.ui.view'].search([('arch_db', 'like', 'modifiers=')])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch
        for old, new in _MODIFIERS_REPLACEMENTS:
            new_arch = new_arch.replace(old, new)
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: `banner_route` (el atributo que mostraba el banner de
# onboarding en la vista lista de facturas) ya no existe en v19; Studio lo
# había agregado por xpath sobre la vista base de facturas
# (`account.out.invoice.tree.invoke_custumers`, sin xmlid, 100% en base de
# datos). El validador lo rechaza directo ("Invalid attribute banner_route
# for element list") e invalida toda la vista. Se quita ese bloque de
# xpath -no hacía falta, era sólo un banner informativo-.
_BANNER_ROUTE_XPATH_RE = re.compile(
    r'<xpath expr="//tree" position="attributes">\s*'
    r'<attribute name="banner_route">[^<]*</attribute>\s*'
    r'</xpath>'
)


def _fix_broken_banner_route(env):
    views = env['ir.ui.view'].search([('arch_db', 'like', 'banner_route')])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _BANNER_ROUTE_XPATH_RE.sub('', arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: `x_area`/`x_area_trabajo` (res.partner) ya se formalizaron
# como código (`_compute_x_area` en `models/res_partner.py`), pero el
# registro `ir.model.fields` que quedó de Studio todavía guarda
# `related='self.opportunity_ids.x_area_lead'` -sintaxis propia de Studio
# ("self." como prefijo del registro actual), nunca válida como `related=`
# real de Odoo-. `_add_manual_fields` sólo debería re-agregar un campo
# manual si el modelo de código NO lo define ya, pero en producción esta
# fila obsoleta sigue disparando el warning "Field 'res.partner.self' ...
# should be searchable" durante recomputaciones en cron -su `related` viejo
# sigue haciendo referencia a un campo "self" que no existe-, algo que en
# las pruebas locales no se reproduce siempre igual, según el orden exacto
# en que se reconstruye el registro. Se limpia el `related` viejo
# directamente para no depender de esa condición de carrera: el campo ya
# vive en código, esta fila no debería seguir describiendo una relación.
def _fix_stale_manual_field_related(env):
    env.cr.execute("""
        UPDATE ir_model_fields
        SET related = NULL, state = 'base'
        WHERE model = 'res.partner' AND name IN ('x_area', 'x_area_trabajo')
        AND related LIKE 'self.%%'
    """)


# MIGRACIÓN V19: estos 4 campos siguen siendo manuales de Studio -no se
# formalizaron a propósito, están fuera de alcance (ver comentario en
# `models/stock.py` para `x_studio_otros_documentos_1`: cruza un
# many2many)-, pero comparten etiqueta entre sí ("Two fields ... have the
# same label"). Sólo se renombra la etiqueta (`field_description`) para
# quitar el warning, sin tocar `state` ni ninguna otra propiedad -no se
# están formalizando aquí, sólo se les pone una etiqueta distinta-.
_DUPLICATE_LABEL_FIELDS = [
    ('sale.order', 'x_productos_si', 'Productos (sí)'),
    ('sale.order', 'x_productos_no', 'Productos (no)'),
    ('stock.picking', 'x_studio_otros_documentos_1', 'Otros Documentos (2)'),
]


def _fix_duplicate_manual_field_labels(env):
    IrModelFields = env['ir.model.fields']
    for model, name, label in _DUPLICATE_LABEL_FIELDS:
        field = IrModelFields.search([
            ('model', '=', model), ('name', '=', name), ('state', '=', 'manual'),
        ], limit=1)
        if field and field.field_description != label:
            field.write({'field_description': label})


def pre_init_hook(env):
    _deactivate_old_studio_report_views(env)
    _fix_accounting_menu_parents(env)
    _cleanup_unused_studio_fields(env)
    _fix_broken_l10n_mx_edi_reports(env)
    _fix_broken_studio_report_field_refs(env)
    _fix_broken_purchase_order_uom_ref(env)
    _fix_broken_purchase_order_notes_ref(env)
    _fix_broken_studio_invoice_report_wrappers(env)
    _fix_broken_invoice_report_display_type(env)
    _fix_broken_tax_totals_json(env)
    _fix_broken_tax_totals_structure(env)
    _fix_broken_modifiers_attribute(env)
    _fix_broken_banner_route(env)
    _fix_stale_manual_field_related(env)
    _fix_duplicate_manual_field_labels(env)
    _reactivate_studio_automations(env)
    _delete_old_studio_account_move_form_view(env)
    _force_install_novu_modules(env)


# MIGRACIÓN V19: estas automatizaciones (`base.automation`, todas sobre
# `sale.order`) son de Odoo Studio (módulos fantasma `studio_customization`/
# `__export__`, sin dueño real). Se observó que en rebuilds de bases de
# prueba de Odoo.sh (bases "neutralizadas") terminan archivadas
# (`active=False`) -no está claro si es un paso adicional de neutralización
# propio de la plataforma, ya que el `neutralize.sql` del core sólo
# desactiva crons/servidores de correo/webhooks, no `base.automation`
# directamente-. Se reactivan por nombre exacto en cada actualización del
# módulo como red de seguridad, para no depender de hacerlo a mano cada vez.
STUDIO_AUTOMATION_NAMES = [
    'Send mail ventas',
    '*Notificar de aprobaciones pendientes al gerente de ventas Sandra',
    '*Notificar de aprobaciones pendientes al gerente de ventas Raúl',
    'validaciones',
    'Notificación a compras',
    'Quitar cliente de los seguidores',
]


def _reactivate_studio_automations(env):
    automations = env['base.automation'].with_context(active_test=False).search([
        ('name', 'in', STUDIO_AUTOMATION_NAMES),
        ('active', '=', False),
    ])
    if automations:
        automations.write({'active': True})


# MIGRACIÓN V19: esta es la vista que Odoo Studio generó automáticamente
# para las personalizaciones de `account.view_move_form` (state='manual',
# módulo fantasma `studio_customization`) -es el origen exacto del bloque
# XML que se formalizó campo por campo en `views/account_move_form.xml`,
# confirmado contra su `arch_db` real-. Está inactiva, pero `active=False`
# NO la excluye de la validación del árbol de vistas heredadas de
# `account.view_move_form`: cualquier actualización de una vista hermana
# (ej. `account_move_proper.view_account_move_form_inherited_dates`) la
# arrastra igual, y su xpath a `l10n_mx_edi_origin` -campo eliminado en
# 19.0- rompe la actualización con "El elemento ... no puede ser
# localizado en la vista padre". Como su contenido ya está 100% cubierto
# por la vista formalizada, se elimina en vez de solo desactivarla o
# parchear su texto (que dejaría otros anclas rotas sin resolver, ej.
# `l10n_mx_edi_cancel_invoice_id`, también removido).
OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID = 'studio_customization.odoo_studio_account__ac74cbfb-da24-46b5-aca5-f72183fdfc26'


def _delete_old_studio_account_move_form_view(env):
    view = env.ref(OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID, raise_if_not_found=False)
    if view:
        env.cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id = %s", (view.id,))
        env.cr.execute("DELETE FROM ir_ui_view WHERE id = %s", (view.id,))


# MIGRACIÓN V19: `novu_sale_order` y `novu_purchase_order` no existen en
# producción (`PROPER SERVICES`) -se crearon en un intento de migración
# anterior, en una rama de staging-, así que en esta base (restaurada desde
# un backup de producción en cada build) nunca aparecen "instalados" de
# entrada. `auto_install` (ver sus manifests) nunca se dispara para ellos
# por esa misma razón: sólo se activa cuando alguna dependencia pasa a
# instalarse en esa misma operación, y aquí sus dependencias (sale,
# purchase, web_studio, etc.) siempre están instaladas de antes. Se fuerza
# su instalación por código en cada actualización de este módulo -Odoo
# recoge módulos marcados "to install" durante la misma carga del registro
# (ver `odoo/modules/loading.py`, `load_modules`, "STEP 3"), así que
# `button_install()` aquí basta para que terminen instalados al final de
# este mismo build, sin depender de un clic manual que se perdería en el
# siguiente rebuild-.
NOVU_MODULES_TO_FORCE_INSTALL = ['novu_sale_order', 'novu_purchase_order']


def _force_install_novu_modules(env):
    modules = env['ir.module.module'].search([
        ('name', 'in', NOVU_MODULES_TO_FORCE_INSTALL),
        ('state', '=', 'uninstalled'),
    ])
    if modules:
        modules.button_install()


def post_init_hook(env):
    _fix_sale_order_menu_actions(env)
