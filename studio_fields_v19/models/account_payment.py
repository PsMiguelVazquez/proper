# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    x_equipo_ventas_fact = fields.Char(
        string='Equipo(s) de ventas', compute='_compute_x_equipo_ventas_fact')
    x_total_adeudado = fields.Float(
        string='Importe total adeudado de facturas', compute='_compute_x_total_adeudado')
    x_total_facturas = fields.Float(
        string='Importe total  de las facturas', compute='_compute_x_total_facturas')
    x_total_pagado_facturas = fields.Float(
        string='Importe pagado de facturas', compute='_compute_x_total_pagado_facturas')
    x_vendedores = fields.Char(
        string='Vendedor(es)', compute='_compute_x_vendedores')

    @api.depends('reconciled_invoice_ids')
    def _compute_x_equipo_ventas_fact(self):
        for record in self:
            record.x_equipo_ventas_fact = ','.join(
                record.reconciled_invoice_ids.mapped('invoice_user_id.sale_team_id.name'))

    @api.depends('reconciled_invoice_ids')
    def _compute_x_total_adeudado(self):
        for record in self:
            record.x_total_adeudado = sum(record.reconciled_invoice_ids.mapped('amount_residual'))

    @api.depends('reconciled_invoice_ids')
    def _compute_x_total_facturas(self):
        for record in self:
            record.x_total_facturas = sum(record.reconciled_invoice_ids.mapped('amount_total'))

    @api.depends('x_total_facturas', 'x_total_adeudado')
    def _compute_x_total_pagado_facturas(self):
        for record in self:
            record.x_total_pagado_facturas = record.x_total_facturas - record.x_total_adeudado

    @api.depends('reconciled_invoice_ids')
    def _compute_x_vendedores(self):
        for record in self:
            record.x_vendedores = ','.join(record.reconciled_invoice_ids.mapped('invoice_user_id.name'))

    # MIGRACIÓN V19: en v15, "Forma de pago" (`l10n_mx_edi_payment_method_id`)
    # y "CFDI Origen" (`l10n_mx_edi_cfdi_origin`) vivían como campos propios
    # de `account.move`, y la vista de pago de `l10n_mx_edi` los mostraba con
    # una sola condición (`country_code == 'MX'`) - editables desde "Nuevo",
    # sin necesidad de guardar nada (ver `enterprise/l10n_mx_edi/views/
    # account_payment_view.xml` de la base v15).
    #
    # En v19, `l10n_mx_edi/models/account_payment.py` los redefinió como
    # `related='move_id....', readonly=False` (sin `store=True`, o sea sin
    # columna propia), y la vista los envolvió en un grupo "CFDI" con
    # `invisible="not l10n_mx_edi_is_cfdi_needed"` (también un `related` a
    # `move_id...`). El problema: `move_id` (el asiento contable del pago)
    # ya NO se crea al guardar - se crea recién al confirmar el pago
    # (`_generate_journal_entry` en `addons/account/models/
    # account_payment.py`, que en la misma llamada pone `state='in_process'`).
    # Resultado: mientras el pago está en Borrador no hay `move_id` -> el
    # grupo entero es invisible (nada que mostrar); en cuanto se confirma,
    # `move_id` ya existe -> el grupo aparece, pero el campo ya quedó de
    # solo lectura (`readonly="state != 'draft'"`, en la vista). No hay
    # ninguna ventana en la que un pago creado directo (Contabilidad >
    # Clientes > Pagos > Nuevo, no vía el asistente "Registrar Pago" de una
    # factura) permita editar estos 2 campos. Confirmado en pruebas: un pago
    # nuevo, guardado y lleno, sigue sin mostrar el grupo mientras sigue en
    # Borrador.
    #
    # Se restauran como campos propios almacenados (ya no `related`) para
    # que tengan valor -y sean editables- desde antes de que exista
    # `move_id`; `_generate_move_vals` (abajo) los traslada al asiento en
    # cuanto éste se crea, igual que ya hace `l10n_mx_edi`/
    # `account_payment_register.py` con los campos del asistente
    # "Registrar Pago". El resto de la lógica de CFDI (generación del
    # complemento, XML, etc., ver `enterprise/l10n_mx_edi/models/
    # account_move.py`) sigue leyendo siempre `move_id.l10n_mx_edi_*`, no
    # estos campos de `account.payment` - no se toca nada de esa lógica.
    l10n_mx_edi_payment_method_id = fields.Many2one(
        comodel_name='l10n_mx_edi.payment.method',
        string="Forma de pago",
        store=True,
        readonly=False,
        compute='_compute_l10n_mx_edi_payment_method_id_studio',
        help="Indica la forma en la que se pagó/pagará, p.ej. Efectivo, "
             "Cheque nominativo, Transferencia electrónica de fondos, etc.",
    )
    l10n_mx_edi_cfdi_origin = fields.Char(string="CFDI Origen", store=True, readonly=False)

    @api.depends('journal_id')
    def _compute_l10n_mx_edi_payment_method_id_studio(self):
        # Mismo comportamiento por defecto que `account.move` en v15/v19
        # (`_compute_l10n_mx_edi_payment_method_id`): si el usuario no eligió
        # nada todavía, se propone la forma de pago configurada en el
        # diario. No se sobrescribe si ya tiene un valor -manual o de un
        # `journal_id` anterior-.
        for pay in self:
            if not pay.l10n_mx_edi_payment_method_id:
                pay.l10n_mx_edi_payment_method_id = pay.journal_id.l10n_mx_edi_payment_method_id

    def _generate_move_vals(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        # EXTENDS 'account': traslada al asiento contable, en el momento en
        # que se crea (al confirmar), los 2 campos de arriba - de otro modo
        # el asiento nacería sin "Forma de pago"/"CFDI Origen" aunque el
        # usuario ya los hubiera llenado en el pago.
        vals = super()._generate_move_vals(
            write_off_line_vals=write_off_line_vals, force_balance=force_balance, line_ids=line_ids)
        vals['l10n_mx_edi_payment_method_id'] = self.l10n_mx_edi_payment_method_id.id
        vals['l10n_mx_edi_cfdi_origin'] = self.l10n_mx_edi_cfdi_origin
        return vals


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    # MIGRACIÓN V19: en Studio era `related='line_ids.rel_payment'`, pero
    # `line_ids` es `One2many` (puede haber más de un apunte por extracto)
    # y `related=` no soporta atravesar x2many; se reescribe como compute
    # tomando el primer apunte.
    x_pagos_extracto = fields.Many2one(
        'account.payment', string='Pagos extracto', compute='_compute_x_pagos_extracto')

    @api.depends('line_ids.rel_payment')
    def _compute_x_pagos_extracto(self):
        for record in self:
            record.x_pagos_extracto = record.line_ids[:1].rel_payment


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    x_referencia_bancaria = fields.Char(string='Referencia bancaria')
