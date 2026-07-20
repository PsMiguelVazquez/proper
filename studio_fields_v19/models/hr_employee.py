# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # MIGRACIÓN V19: campos manuales de Studio (export "Campos
    # (ir.model.fields) (3)"). No se agregan a ninguna vista -eso quedó
    # fuera de alcance de esta tanda-, sólo se formalizan como campos
    # reales para que no se pierdan en el próximo rebuild.
    x_studio_centro_de_costos = fields.Char(string='Centro de costos')
    x_studio_responder_a = fields.Many2one('hr.employee', string='Reportar a')
    x_studio_nmero_de_seguro = fields.Char(string='Número de seguro')
    x_studio_curp = fields.Char(string='CURP')
    x_studio_porcentaje = fields.Float(string='Porcentaje')
    x_studio_parentesco = fields.Char(string='Parentesco')
    x_studio_nombre_del_padre = fields.Char(string='Nombre del padre')
    x_studio_fecha_de_vencimiento = fields.Date(string='Fecha de vencimiento')
    x_studio_fecha_de_nacimiento = fields.Date(string='Fecha de nacimiento')
    x_studio_nombre_de_la_madre = fields.Char(string='Nombre de la madre')
    x_studio_nombre_del_beneficiario = fields.Char(string='Nombre del beneficiario')
    x_studio_n_de_licencia_1 = fields.Char(string='N° de licencia')
    x_studio_fecha_de_alta = fields.Date(string='Fecha de alta')
    x_studio_fecha_de_baja = fields.Date(string='Fecha de baja')
    x_studio_recomendado_por = fields.Char(string='Recomendado por')
    x_studio_reclutador = fields.Many2one('hr.employee', string='Reclutador')
    x_studio_fecha_de_antigedad = fields.Date(string='Fecha de antigüedad')
    x_studio_estatus = fields.Selection(
        [('Planta', 'Planta'), ('Temporal', 'Temporal'), ('Honorarios', 'Honorarios')], string='Estatus')

    # MIGRACIÓN V19: modelos propios de Studio `x_conceptos_de_baja`/
    # `x_conceptos_basicos_de`, formalizados en
    # `sale_purchase_confirm/models/custom_models.py`.
    x_studio_concepto_de_baja_1 = fields.Many2one('x_conceptos_de_baja', string='Concepto de baja')
    x_studio_many2one_field_7FEJz = fields.Many2one(
        'x_conceptos_basicos_de', string='Conceptos básicos de operación')

    # MIGRACIÓN V19: en Studio era `related='user_id.vat'` (`Many2one`).
    x_studio_rfc = fields.Char(related='user_id.vat', store=True, string='RFC')
