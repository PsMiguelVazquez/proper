# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_missing_batch_payment_sequence` en
`__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo para
el detalle completo (por qué `res.company.batch_payment_sequence_id`
queda vacío en compañías que vienen de un backup de v15).
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
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
