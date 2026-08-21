import re

from lxml import etree

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


# MIGRACIÓN V19: la herramienta oficial de upgrade de Odoo (usada para
# migrar el backup de PRD -v15- a esta rama de pruebas) convirtió una
# personalización vieja de assets -en v15, una vista que insertaba
# `<script src=".../account_payment_field.js">` directo en el bundle del
# backend- a un registro `ir.asset` nuevo (nombre autogenerado tipo
# "account_payment_widget_amount.assets_backend--view_id:3927--1"). Ese
# archivo ya no existe: se renombró a `account_payment_field_patch.js` al
# reescribir el widget de `odoo.define`/AbstractField a un componente OWL
# (ver `account_payment_widget_amount/static/src/js/
# account_payment_field_patch.js`). El `ir.asset` viejo sigue intentando
# incluirlo en cada bundle del backend, y como el archivo no existe, el
# navegador falla al cargarlo -lo que puede romper en cascada el resto del
# bundle que carga después, incluyendo botones/widgets que no tienen nada
# que ver con pagos (confirmado: así se manifestaba, un botón "Reservar"
# del reporte pronosticado que no hacía ninguna llamada al servidor)-.
# Como este registro lo regenera la propia herramienta de upgrade cada vez
# que se restaura el backup de PRD sobre esta rama, se desactiva aquí en
# cada arranque del registro en vez de depender de que alguien lo
# desactive a mano después de cada intento de upgrade.
# `like` (no `in`) a propósito: la ruta que genera la herramienta de
# upgrade trae un `/` inicial (`/account_payment_widget_amount/...`,
# confirmado en la base real), y un `in` con la ruta exacta sin esa barra
# no encontraba el registro. `like` hace un `contains`, así que calza con
# o sin el `/` inicial. No hay riesgo de que también atrape al archivo
# nuevo (`account_payment_field_patch.js`): esa cadena no es substring de
# esta ("field.js" != "field_patch.js").
STALE_UPGRADE_ASSET_PATH = 'account_payment_widget_amount/static/src/js/account_payment_field.js'


def _deactivate_stale_upgrade_asset_overrides(env):
    assets = env['ir.asset'].search([
        ('path', 'like', STALE_UPGRADE_ASSET_PATH),
        ('active', '=', True),
    ])
    if assets:
        assets.write({'active': False})


# MIGRACIÓN V19: `res.company.batch_payment_sequence_id` (`addons/account/
# models/company.py`) sólo tiene `default=`, sin `compute=` -Odoo únicamente
# corre ese `default` al CREAR una compañía nueva, nunca lo rellena
# retroactivamente en compañías que ya existían antes de que este campo se
# agregara al core (introducido varias versiones después de v15). El
# resultado: la compañía real (viene del backup de v15) quedó con este
# campo vacío, y el core no valida eso antes de usarlo -`get_next_batch_
# payment_communication()` llama `self.sudo().batch_payment_sequence_id.
# next_by_id()` sin comprobar que exista-, lo que revienta con
# "psycopg2.errors.UndefinedFunction: operator does not exist: integer =
# boolean" (intenta `... WHERE id=false`) al confirmar el asistente
# "Registrar Pago" desde la lista de facturas. Se crea la secuencia
# faltante con los mismos valores que usa el `default=` del core, para
# cualquier compañía a la que le falte.
def _fix_missing_batch_payment_sequence(env):
    IrSequence = env['ir.sequence'].sudo()
    for company in env['res.company'].sudo().search([('batch_payment_sequence_id', '=', False)]):
        company.batch_payment_sequence_id = IrSequence.create({
            'name': "Group Payments Number Sequence",
            'implementation': 'no_gap',
            'padding': 5,
            'use_date_range': True,
            'company_id': company.id,
            'prefix': 'GROUP/%(year)s/',
        })


# MIGRACIÓN V19: `carta_porte.view_picking_carta_porte` (inserta "Fecha de
# recepción del cliente"/"Persona que recibe" en el formulario de
# traslados, justo después de `location_dest_id`) aparece con
# `active=False` sin causa rastreable -mismo fenómeno de menús/
# automatizaciones de Studio que ya se ve varias veces en este archivo,
# tras un rebuild/restauración de Odoo.sh-. Confirmado que el módulo y el
# campo sí están instalados (Studio los ofrece como "campos existentes"
# en el editor de vistas); sólo la vista que los inserta en el formulario
# queda inactiva, así que el formulario se ve completo pero sin estos 2
# campos.
CARTA_PORTE_VIEW_XMLIDS = [
    'carta_porte.view_picking_carta_porte',
]


def _reactivate_carta_porte_views(env):
    for xmlid in CARTA_PORTE_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view and not view.active:
            view.write({'active': True})


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


# MIGRACIÓN V19: el menú "Contabilidad > Clientes > Facturas"
# (`account.menu_action_move_out_invoice_type`) mostraba facturas Y notas
# de crédito revueltas en la misma lista, sin el filtro que trae hoy el
# core. El core reemplazó, hace varias versiones, la acción original de
# ese menú (`account.action_move_out_invoice_type` -domain `move_type in
# (out_invoice, out_refund, out_receipt)`, SIN filtro activo por defecto
# en el buscador-) por una nueva `account.action_move_out_invoice` (mismo
# domain, pero con `context={'search_default_out_invoice': 1,
# 'search_default_out_receipt': 1, ...}`, que sí excluye las notas de
# crédito por defecto vía el buscador -ver
# `addons/account/views/account_move_views.xml` y el `<menuitem>` de
# `addons/account/views/account_menuitem.xml`, que ya usa la acción
# nueva-). El menú de esta base quedó `noupdate=True` (todo lo que toca
# Studio termina así) apuntando todavía a la acción vieja de antes de la
# migración, así que el upgrade de `account` nunca lo re-apunta solo -un
# `<record>` en un XML de datos tampoco alcanzaría, mismo motivo que
# `_fix_accounting_menu_parents`/`_fix_sale_order_menu_actions`-.
def _fix_customer_invoice_menu_action(env):
    menu = env.ref('account.menu_action_move_out_invoice_type', raise_if_not_found=False)
    action = env.ref('account.action_move_out_invoice', raise_if_not_found=False)
    if not (menu and action):
        return
    action_ref = 'ir.actions.act_window,%d' % action.id
    # Ver el comentario en `_fix_sale_order_menu_actions` sobre por qué se
    # compara recordset contra recordset (evita el `UserWarning` de
    # `BaseModel.__eq__` al comparar un campo `Reference` roto/vacío
    # contra un string).
    current_action = menu.action
    if not (current_action and current_action._name == action._name and current_action.id == action.id):
        menu.write({'action': action_ref})


# MIGRACIÓN V19: `models/account_payment.py` redefine
# `l10n_mx_edi_payment_method_id`/`l10n_mx_edi_cfdi_origin` en
# `account.payment` de `related` (sin columna propia) a campos propios
# almacenados (ver ese archivo para el porqué completo). Al agregar la
# columna por primera vez, todo pago YA confirmado antes de instalar este
# cambio queda con esos 2 campos en NULL -aunque el asiento (`move_id`) sí
# tenga los valores reales-, así que sin este backfill esos pagos viejos
# se verían con "Forma de pago"/"CFDI Origen" vacíos en la vista (aunque
# el CFDI ya esté timbrado correctamente con el valor real). Se copia
# desde `move_id` una sola vez por registro -sólo rellena huecos, nunca
# pisa un valor que ya esté puesto-.
# "99 - Por definir" (`l10n_mx_edi.payment_method_otros`) se reactiva a
# pedido del cliente, para poder elegirla a mano en el desplegable de
# "Forma de pago" cuando de verdad no se conoce la forma de pago real.
# Odoo la instala inactiva a propósito -es el código SAT de "forma de pago
# no identificada"-, ver `enterprise/l10n_mx_edi/data/
# l10n_mx_edi_payment_method_data.xml`; confirmado que activarla no
# cambia ningún default ni validación de timbrado (`account_move.py`
# busca este código puntual con `active_test=False` a propósito, o sea ya
# asume que puede estar inactivo), sólo si aparece en el buscador para
# selección manual. Ese XML de `l10n_mx_edi` tiene `noupdate="0"`, así que
# cualquier `-u l10n_mx_edi` que corra sin pasar también por este módulo
# la vuelve a dejar en `active=False`; se reactiva aquí en cada arranque
# del registro para que el cambio no se "pierda".
def _activate_payment_method_otros(env):
    payment_method = env.ref('l10n_mx_edi.payment_method_otros', raise_if_not_found=False)
    if payment_method and not payment_method.active:
        payment_method.write({'active': True})


def _backfill_payment_mx_edi_fields(env):
    payments = env['account.payment'].search([
        ('move_id', '!=', False),
        '|',
        ('l10n_mx_edi_payment_method_id', '=', False),
        ('l10n_mx_edi_cfdi_origin', '=', False),
    ])
    for payment in payments:
        vals = {}
        if not payment.l10n_mx_edi_payment_method_id and payment.move_id.l10n_mx_edi_payment_method_id:
            vals['l10n_mx_edi_payment_method_id'] = payment.move_id.l10n_mx_edi_payment_method_id.id
        if not payment.l10n_mx_edi_cfdi_origin and payment.move_id.l10n_mx_edi_cfdi_origin:
            vals['l10n_mx_edi_cfdi_origin'] = payment.move_id.l10n_mx_edi_cfdi_origin
        if vals:
            payment.write(vals)


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
        # MIGRACIÓN V19: `menu.action` (campo `Reference`) puede resolver a
        # un recordset vacío (`ir.actions.act_window()`, no `False`) cuando
        # la referencia guardada apunta a un id que ya no existe. Comparar
        # ese recordset contra el string `action_ref` con `!=` dispara un
        # `UserWarning` de `BaseModel.__eq__`
        # (`unsupported operand type(s) for "==": ...`) -no rompe nada, el
        # `if` igual evalúa como distinto y corrige el menú, pero ensucia
        # el log y hace que Odoo.sh marque el build/deploy en amarillo-.
        # Se compara recordset contra recordset (nunca contra el string)
        # para evitar el warning por completo.
        current_action = menu.action
        if not (current_action and current_action._name == action._name and current_action.id == action.id):
            menu.write({'action': action_ref})
        # MIGRACIÓN V19: estos 3 menús (Cotizaciones/Pedidos/Marketplace,
        # todos hijos de "Contabilidad > Ventas") aparecen desactivados en
        # la base real sin causa rastreable en el código -mismo fenómeno
        # ya visto varias veces esta sesión-. "Marketplace" concretamente
        # se encontró `active=False` mientras sus 2 hermanos seguían
        # activos, haciendo que dejara de mostrarse en el menú aunque el
        # registro siguiera existiendo. Se reactivan los 3 como red de
        # seguridad en cada actualización del módulo.
        if not menu.active:
            menu.write({'active': True})


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


# MIGRACIÓN V19: mismo patrón que `_fix_broken_l10n_mx_edi_reports` de
# arriba, para otro par de renombres del core -esta vez en `stock.picking`,
# no relacionados con `l10n_mx_edi`-. `move_lines` se renombró a `move_ids`
# hace varias versiones; `move_ids_without_package` se eliminó por completo
# (el core ya no distingue "movimientos sin paquete" con un campo aparte,
# ver `addons/stock/report/report_deliveryslip.xml`, que hoy filtra sobre
# `move_ids` directo). Los reportes de Studio duplicados (remisión,
# document de entrega, carta porte, etc.) copiaron el contenido de v15 tal
# cual y quedaron con los nombres viejos, rompiendo con "'stock.picking'
# object has no attribute 'move_lines'"/"...'move_ids_without_package'" al
# imprimir. Se usa límite de palabra (`\b`) para no tocar por accidente
# variables QWeb que sólo contienen "move_lines" como substring (ej.
# `package_move_lines`, `aggregated_move_lines`, ambas reales en el core).
#
# Los mismos reportes también arrastran otros 4 renombres de campo del
# core, descubiertos al corregir los de arriba (quedaban "debajo" del
# primer error, sin alcanzar a ejecutarse):
#   - `stock.move.line.qty_done`/`quantity_done` -> `quantity` (la cantidad
#     "hecha" ya no es un campo aparte, ver `addons/stock/models/
#     stock_move_line.py`).
#   - `stock.picking.move_line_ids_without_package` -> `move_line_ids`
#     (mismo caso que `move_ids_without_package` de arriba, pero para las
#     líneas de movimiento en vez de los movimientos).
#   - `stock.picking.l10n_mx_edi_status` -> `l10n_mx_edi_cfdi_state` (ver
#     `enterprise/l10n_mx_edi_stock/models/stock_picking.py`).
#   - `fleet.vehicle.transport_perm_sct` -> `l10n_mx_transport_perm_sct`,
#     `fleet.vehicle.transport_insurer` -> `l10n_mx_transport_insurer` (ver
#     `enterprise/l10n_mx_edi_stock/models/fleet_vehicle.py`; todos los
#     campos de carta porte en ese modelo llevan el prefijo `l10n_mx_` que
#     Studio no copió).
#   - `stock.picking.package_level_ids` -> sin reemplazo posible: el
#     modelo `stock.package_level` se eliminó por completo del core (ya no
#     existe ninguna relación equivalente desde `stock.picking`). Sólo se
#     usaba para mostrar una tabla opcional de "paquetes completos"
#     (`t-if="o.package_level_ids and o.picking_type_entire_packs and ..."`
#     seguido de `t-foreach="o.package_level_ids...."` dentro de esa misma
#     tabla); se reemplaza la expresión completa (`<algo>.package_level_
#     ids`, no sólo el nombre del campo) por el literal `False`, para que
#     la tabla simplemente no se muestre -no hay forma de reconstruir la
#     funcionalidad original sin ese modelo-. Reemplazar sólo el nombre
#     del campo dejaría `o.False` (`o.` seguido de la palabra reservada
#     `False`), que es sintaxis Python inválida; hay que consumir también
#     el `<objeto>.` que lo precede. Como QWeb no evalúa el contenido de
#     un elemento cuyo `t-if` da `False`, el `t-foreach` interno nunca
#     llega a ejecutarse contra ese `False`.
#   - `stock.move.line.description_bom_line` -> `description_picking`
#     (related a `move_id.description_picking`, ver `addons/stock/models/
#     stock_move_line.py`); es el campo real que muestra la descripción
#     del producto en los reportes de traslado, `description_bom_line` no
#     existe en ningún módulo instalado.
#   - `stock.move.reserved_availability` -> `quantity` (el core ya no
#     mantiene ese campo aparte; internamente calcula lo mismo como
#     `{move: move.quantity for move in self}`, ver `addons/stock/models/
#     stock_move.py`).
#   - `fleet.vehicle.transport_insurance_policy` ->
#     `l10n_mx_transport_insurance_policy` (mismo caso que
#     `transport_perm_sct`/`transport_insurer` de arriba).
#   - Vista huérfana de Studio (`studio_customization.odoo_studio_report_
#     p_cb1a4aec-...`, heredando por xpath de `report_picking_copy_2_
#     copy_1`/"remisión con costo"): ya hacía
#     `t-set="tax_totals" t-value="o.sale_id.tax_totals"` antes de llamar
#     a `account.document_tax_totals` -el patrón nativo correcto, calcular
#     los totales reales desde la venta ligada, en vez de intentar
#     reconstruirlos a mano-, pero sin guarda para cuando la entrega no
#     tiene venta ligada: con `o.sale_id` vacío, `tax_totals` da `False`
#     (recordset vacío -> valor "vacío" del campo Binary) y
#     `account.document_tax_totals` truena con "'bool' object is not
#     subscriptable" al intentar `tax_totals['subtotals']`. Se agrega
#     `t-if="o.sale_id"` al `<div class="row">` que envuelve esa tabla,
#     para que sólo se muestre cuando sí hay una venta de la que sacar los
#     totales.
#   - `fleet.vehicle.vehicle_licence` -> `license_plate` (campo estándar
#     de `fleet.vehicle`, no lleva prefijo `l10n_mx_` -no es un campo
#     propio de carta porte, es la placa del vehículo en general-, ver
#     `addons/fleet/models/fleet_vehicle.py`).
#   - `fleet.vehicle.vehicle_model` -> `model_id` (Many2one a
#     `fleet.vehicle.model`; no existe un campo de texto aparte, `t-field`
#     sobre un Many2one renderiza su nombre automáticamente).
#   - `fleet.vehicle.figure_ids` -> `l10n_mx_figure_ids` (One2many de
#     carta porte, ver `enterprise/l10n_mx_edi_stock/models/
#     fleet_vehicle.py`; a diferencia de `vehicle_licence`/`vehicle_model`
#     éste sí lleva el prefijo `l10n_mx_`).
_STOCK_PICKING_MOVE_LINES_RE = re.compile(r'\bmove_lines\b')
_STOCK_PICKING_MOVE_WITHOUT_PACKAGE_RE = re.compile(r'\bmove_ids_without_package\b')
_STOCK_PICKING_QTY_DONE_RE = re.compile(r'\b(?:qty_done|quantity_done)\b')
_STOCK_PICKING_MOVE_LINE_WITHOUT_PACKAGE_RE = re.compile(r'\bmove_line_ids_without_package\b')
_STOCK_PICKING_L10N_MX_EDI_STATUS_RE = re.compile(r'\bl10n_mx_edi_status\b')
_STOCK_PICKING_TRANSPORT_PERM_SCT_RE = re.compile(r'\btransport_perm_sct\b')
_STOCK_PICKING_TRANSPORT_INSURER_RE = re.compile(r'\btransport_insurer\b')
_STOCK_PICKING_PACKAGE_LEVEL_IDS_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_.()]*\.package_level_ids')
_STOCK_PICKING_DESCRIPTION_BOM_LINE_RE = re.compile(r'\bdescription_bom_line\b')
_STOCK_PICKING_RESERVED_AVAILABILITY_RE = re.compile(r'\breserved_availability\b')
_STOCK_PICKING_TRANSPORT_INSURANCE_POLICY_RE = re.compile(r'\btransport_insurance_policy\b')
_STOCK_PICKING_TAX_TOTALS_ROW_RE = re.compile(
    r'(<div class="row">)(\s*<div class="col-5"/>\s*<div class="col-5 offset-2">'
    r'\s*<table[^>]*>\s*<t t-set="tax_totals" t-value="o\.sale_id\.tax_totals"/>)'
)
_STOCK_PICKING_VEHICLE_LICENCE_RE = re.compile(r'\bvehicle_licence\b')
_STOCK_PICKING_VEHICLE_MODEL_RE = re.compile(r'\bvehicle_model\b')
_STOCK_PICKING_FIGURE_IDS_RE = re.compile(r'\bfigure_ids\b')


def _fix_broken_stock_picking_reports(env):
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
        ('arch_db', 'like', 'move_lines'),
        ('arch_db', 'like', 'move_ids_without_package'),
        ('arch_db', 'like', 'qty_done'),
        ('arch_db', 'like', 'quantity_done'),
        ('arch_db', 'like', 'l10n_mx_edi_status'),
        ('arch_db', 'like', 'transport_perm_sct'),
        ('arch_db', 'like', 'transport_insurer'),
        ('arch_db', 'like', 'package_level_ids'),
        ('arch_db', 'like', 'description_bom_line'),
        ('arch_db', 'like', 'reserved_availability'),
        ('arch_db', 'like', 'transport_insurance_policy'),
        ('arch_db', 'like', 'o.sale_id.tax_totals'),
        ('arch_db', 'like', 'vehicle_licence'),
        ('arch_db', 'like', 'vehicle_model'),
        ('arch_db', 'like', 'figure_ids'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _STOCK_PICKING_MOVE_LINE_WITHOUT_PACKAGE_RE.sub('move_line_ids', arch)
        new_arch = _STOCK_PICKING_MOVE_LINES_RE.sub('move_ids', new_arch)
        new_arch = _STOCK_PICKING_MOVE_WITHOUT_PACKAGE_RE.sub('move_ids', new_arch)
        new_arch = _STOCK_PICKING_QTY_DONE_RE.sub('quantity', new_arch)
        new_arch = _STOCK_PICKING_L10N_MX_EDI_STATUS_RE.sub('l10n_mx_edi_cfdi_state', new_arch)
        new_arch = _STOCK_PICKING_TRANSPORT_PERM_SCT_RE.sub('l10n_mx_transport_perm_sct', new_arch)
        new_arch = _STOCK_PICKING_TRANSPORT_INSURER_RE.sub('l10n_mx_transport_insurer', new_arch)
        new_arch = _STOCK_PICKING_PACKAGE_LEVEL_IDS_RE.sub('False', new_arch)
        new_arch = _STOCK_PICKING_DESCRIPTION_BOM_LINE_RE.sub('description_picking', new_arch)
        new_arch = _STOCK_PICKING_RESERVED_AVAILABILITY_RE.sub('quantity', new_arch)
        new_arch = _STOCK_PICKING_TRANSPORT_INSURANCE_POLICY_RE.sub('l10n_mx_transport_insurance_policy', new_arch)
        new_arch = _STOCK_PICKING_TAX_TOTALS_ROW_RE.sub(r'<div class="row" t-if="o.sale_id">\2', new_arch)
        new_arch = _STOCK_PICKING_VEHICLE_LICENCE_RE.sub('license_plate', new_arch)
        new_arch = _STOCK_PICKING_VEHICLE_MODEL_RE.sub('model_id', new_arch)
        new_arch = _STOCK_PICKING_FIGURE_IDS_RE.sub('l10n_mx_figure_ids', new_arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})


# MIGRACIÓN V19: mismo tipo de bug preexistente de Studio que
# `_fix_broken_studio_report_field_refs` de abajo (getattr silencioso en
# v15, `KeyError` real en v19), pero en el reporte "Complemento de Pago"
# (Contabilidad > Clientes > Pagos > engrane > Complemento de Pago). La
# personalización de Studio agrega varios campos directo sobre `o` -el
# `account.payment`- que en realidad sólo existen en `account.move`:
# - `o.l10n_mx_edi_post_time` (`enterprise/l10n_mx_edi/models/account_move.py`)
# - `o.serie`/`o.folio` (`sale_purchase_confirm/models/account_move.py`,
#   campos propios calculados con `compute="set_folio"`)
# - `o.l10n_mx_edi_usage` (`enterprise/l10n_mx_edi/models/account_move.py`;
#   sólo se usa detrás de un `t-if="res_company.name=='True'"` -una
#   condición de Studio rota que nunca es cierta en la práctica, ya que
#   compara el nombre de la compañía contra el string "True"-, así que no
#   truena hoy, pero revienta apenas alguien corrija esa condición)
# El resto de esa misma plantilla (la base, no la personalización) sí
# accede correctamente a los campos CFDI vía `o.move_id.XXX`
# (`o.move_id.l10n_mx_edi_cfdi_uuid`, `o.move_id.l10n_mx_edi_cfdi_state`,
# etc.), así que fue un descuido puntual de quien agregó estas líneas en
# Studio -les faltó anteponer `.move_id.`-.
#
# Además, la misma personalización usa
# `cfdi_vals['cfdi_node'].Complemento.xpath(...)` para ubicar los nodos
# `DoctoRelacionado` del XML de pago (repetido varias veces en la
# plantilla). `cfdi_node` viene de `l10n_mx_edi.document.
# _decode_cfdi_attachment()` (`enterprise/l10n_mx_edi/models/
# l10n_mx_edi_document.py`), que en 19.0 lo arma con
# `etree.fromstring()` -un `lxml.etree._Element` normal-, no con
# `lxml.objectify` como asumía Studio; `.Complemento` como atributo
# (acceso estilo objectify) ya no existe ahí y truena con "'lxml.etree.
# _Element' object has no attribute 'Complemento'". El `.xpath('//...')`
# que sigue ya busca en TODO el documento sin importar desde qué nodo se
# llame -confirmado por prueba directa-, así que quitar el salto
# `.Complemento` produce exactamente el mismo resultado.
#
# La plantilla BASE de este reporte (no sólo la personalización -también
# es un duplicado crudo de Studio, `studio_customization.
# report_payment_recei_ddb786bf-f51e-484e-b163-2aa45af1a8c8`-) tiene el
# mismo problema con
# `o.l10n_mx_edi_cfdi_supplier_rfc`/`o.l10n_mx_edi_cfdi_customer_rfc`
# (código de barras QR y bloque "XML VAT"): sólo existen en
# `account.move` (`enterprise/l10n_mx_edi/models/account_move.py`), a
# diferencia de `l10n_mx_edi_cfdi_uuid`, que sí es un `related` válido en
# `account.payment` (`enterprise/l10n_mx_edi/models/account_payment.py`)
# y por eso NO se toca aquí.
#
# IMPORTANTE: a diferencia de `o.l10n_mx_edi_post_time`/`o.serie`/
# `o.folio` (nombres específicos de este módulo, sin colisión conocida),
# `l10n_mx_edi_cfdi_supplier_rfc`/`l10n_mx_edi_cfdi_customer_rfc` SÍ
# aparecen, de forma legítima, en otros reportes core/enterprise no
# relacionados donde `o` es `account.move` -ahí el campo existe tal cual,
# sin `.move_id.`- (ej. `l10n_mx_edi_extended.report_invoice_document`,
# que además tiene otra vista que ubica un elemento suyo por xpath
# buscando el texto exacto del atributo -`(//span[@t-out='o.l10n_mx_edi_
# cfdi_customer_rfc or o.partner_id.vat'])[1]`-, así que reescribir esa
# cadena en el lugar equivocado no sólo introduce un bug nuevo, rompe la
# actualización entera con "cannot be located in parent view"). Por eso
# esta función ya NO busca por contenido en TODAS las vistas qweb: sólo
# toca las dos vistas conocidas de este reporte, por xmlid exacto.
_PAYMENT_RECEIPT_MOVE_FIELD_RE = re.compile(
    r'\bo\.(serie|folio|l10n_mx_edi_usage|l10n_mx_edi_post_time'
    r'|l10n_mx_edi_cfdi_supplier_rfc|l10n_mx_edi_cfdi_customer_rfc)\b'
)

PAYMENT_RECEIPT_STUDIO_VIEW_XMLIDS = [
    'studio_customization.report_payment_recei_ddb786bf-f51e-484e-b163-2aa45af1a8c8',
    'studio_customization.odoo_studio_report_p_74cc6f4f-6ec6-4230-aaa5-d5c47e377cf4',
]


def _fix_broken_payment_receipt_post_time_ref(env):
    for xmlid in PAYMENT_RECEIPT_STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if not view or view.type != 'qweb' or not view.arch_db:
            continue
        arch = view.arch_db
        new_arch = _PAYMENT_RECEIPT_MOVE_FIELD_RE.sub(r'o.move_id.\1', arch)
        new_arch = new_arch.replace('.Complemento.xpath(', '.xpath(')
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


# MIGRACIÓN V19: subconjunto de las funciones de más abajo que es seguro
# repetir en CUALQUIER momento, no sólo durante instalación/upgrade -todas
# comprueban el estado actual antes de escribir-. Se excluye a propósito
# `_force_install_novu_modules`: marcar un módulo "to install" sólo tiene
# efecto real si ocurre dentro del mismo `load_modules()` que hace STEP 3
# (`odoo/modules/loading.py`), que recoge módulos "to install" y los carga
# en esa misma pasada; llamarlo fuera de ahí (p.ej. desde `_register_hook`,
# que corre en STEP 9, después) sólo dejaría el módulo a medio marcar sin
# instalarlo de verdad. Ver `models/self_heal.py` para el otro llamador de
# esta lista, pensado para correr en cada arranque del registro y no sólo
# cuando la versión del módulo "sube".
def _self_heal_idempotent_fixes(env):
    _deactivate_old_studio_report_views(env)
    _deactivate_stale_upgrade_asset_overrides(env)
    _fix_missing_batch_payment_sequence(env)
    _reactivate_carta_porte_views(env)
    _fix_accounting_menu_parents(env)
    _fix_customer_invoice_menu_action(env)
    _activate_payment_method_otros(env)
    _backfill_payment_mx_edi_fields(env)
    _cleanup_unused_studio_fields(env)
    _fix_broken_l10n_mx_edi_reports(env)
    _fix_broken_stock_picking_reports(env)
    _fix_broken_studio_report_field_refs(env)
    _fix_broken_payment_receipt_post_time_ref(env)
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
    _fix_studio_sale_order_tree_columns_scope(env)
    _restore_studio_quotation_tree_columns(env)
    _fix_studio_quotation_tree_columns_anchor(env)
    _fix_sale_order_menu_actions(env)


def pre_init_hook(env):
    _self_heal_idempotent_fixes(env)
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


# MIGRACIÓN V19: "Mis presupuestos" (Ventas) mostraba columnas que en
# producción (15.0) sólo pertenecen a "Pedidos" (Almacén, Cant. Solicitada/
# Asignada/Entregada/x Entregar, Estado de surtido, Método de entrega,
# Documentos de entrega, Estado de almacén de entrega, botón "Generar
# Orden") -confirmado comparando capturas reales de producción: en 15.0
# "Presupuestos" SÍ muestra "N° Orden de compra"/"Estado de compras", pero
# NO las columnas de logística de entrega (tiene sentido: una cotización
# sin confirmar no tiene albarán todavía)-.
#
# Causa real: la vista de Studio que agrega las columnas de logística
# (`odoo_studio_sale_ord_f72ed18a-...`) cuelga de `sale.sale_order_tree`
# -la raíz COMPARTIDA por "Pedidos" (`sale.view_order_tree`) y
# "Presupuestos" (`sale.view_quotation_tree`)-, en vez de colgar
# específicamente de `sale.view_order_tree` como en la base de producción
# original. Probablemente un efecto del proceso de upgrade oficial de
# Odoo (15.0 no tenía esta separación en tres niveles raíz/pedidos/
# presupuestos; el upgrade tuvo que remapear el `inherit_id` original a
# algo en 19.0, y remapeó a la raíz compartida en vez de al nodo
# específico). Se reasigna por código al nodo correcto.
STUDIO_SALE_ORDER_TREE_COLUMNS_XMLID = 'studio_customization.odoo_studio_sale_ord_f72ed18a-41b5-433e-a8f1-73221ffd3c98'


def _fix_studio_sale_order_tree_columns_scope(env):
    view = env.ref(STUDIO_SALE_ORDER_TREE_COLUMNS_XMLID, raise_if_not_found=False)
    order_tree = env.ref('sale.view_order_tree', raise_if_not_found=False)
    if not view or not order_tree:
        return
    if view.inherit_id.id != order_tree.id:
        view.write({'inherit_id': order_tree.id})


# MIGRACIÓN V19: deshace el fix `_fix_duplicate_quotation_tree_columns` de
# una versión anterior de este módulo -diagnóstico incorrecto: asumía que
# `x_studio_n_orden_de_compra`/`x_estado_compra` en esta vista eran
# duplicados a eliminar, cuando en realidad SÍ pertenecen a "Presupuestos"
# en producción (ver comentario arriba). El problema de fondo era la vista
# de Studio equivocada (`_fix_studio_sale_order_tree_columns_scope`, ya
# corregida). Se restauran ambos campos si faltan, sin duplicarlos si ya
# están (p.ej. builds nuevos donde el fix incorrecto nunca corrió).
DUPLICATE_QUOTATION_TREE_VIEW_XMLID = 'studio_customization.odoo_studio_sale_ord_5540e2f3-8cc7-4a6b-800a-7db9408fe51d'


def _restore_studio_quotation_tree_columns(env):
    view = env.ref(DUPLICATE_QUOTATION_TREE_VIEW_XMLID, raise_if_not_found=False)
    if not view or not view.arch_db:
        return
    try:
        root = etree.fromstring(view.arch_db.encode())
    except etree.XMLSyntaxError:
        return
    changed = False

    if root.find(".//xpath[@expr=\"//list[1]/field[@name='name']\"]") is None:
        xpath_node = etree.Element('xpath')
        xpath_node.set('expr', "//list[1]/field[@name='name']")
        xpath_node.set('position', 'after')
        field = etree.SubElement(xpath_node, 'field')
        field.set('name', 'x_studio_n_orden_de_compra')
        field.set('optional', 'show')
        root.insert(0, xpath_node)
        changed = True

    if root.find(".//field[@name='x_estado_compra']") is None:
        currency_xpath = root.find(".//xpath[@expr=\"//field[@name='currency_id']\"]")
        if currency_xpath is not None:
            field = etree.Element('field')
            field.set('name', 'x_estado_compra')
            comentarios = currency_xpath.find("field[@name='x_studio_comentarios']")
            if comentarios is not None:
                comentarios.addnext(field)
            else:
                currency_xpath.append(field)
            changed = True

    if changed:
        view.write({'arch_db': etree.tostring(root, encoding='unicode')})


# MIGRACIÓN V19: en la base de producción (15.0), "Estados de propuestas"/
# "Estado de compras" (agregados por la vista de arriba con
# `position="after"` sobre `currency_id`) aparecían al FINAL de la fila de
# "Mis presupuestos", coincidiendo con la captura real de producción. En
# 19.0 el core movió la declaración de `currency_id` en la vista base
# `sale.sale_order_tree` (`addons/sale/views/sale_order_views.xml`) al
# PRINCIPIO de la lista -es un campo invisible (`column_invisible`), sólo
# ahí para que esté disponible temprano para el widget Monetary de otros
# campos, pero su posición en el XML sigue determinando dónde caen los
# campos insertados "después" de él-. El xpath de Studio sigue apuntando
# literalmente a `currency_id`, así que ahora esas dos columnas aparecen
# al PRINCIPIO en vez de al final -un efecto colateral de un cambio propio
# del core, no de este proyecto-. Se reancla al final de la fila,
# usando `invoice_status` (el último campo visible de la base) como
# referencia, para reproducir la posición real de producción.
def _fix_studio_quotation_tree_columns_anchor(env):
    view = env.ref(DUPLICATE_QUOTATION_TREE_VIEW_XMLID, raise_if_not_found=False)
    if not view or not view.arch_db:
        return
    try:
        root = etree.fromstring(view.arch_db.encode())
    except etree.XMLSyntaxError:
        return
    xpath_node = root.find(".//xpath[@expr=\"//field[@name='currency_id']\"]")
    if xpath_node is None:
        return
    xpath_node.set('expr', "//field[@name='invoice_status']")
    view.write({'arch_db': etree.tostring(root, encoding='unicode')})


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
