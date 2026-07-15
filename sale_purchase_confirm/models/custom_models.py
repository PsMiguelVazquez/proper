# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: `x_fabricante`, `x_familia`, `x_linea` y `x_grupo` eran
modelos propios creados enteramente con Odoo Studio en la base de datos de
producción de v15 (sin código de módulo), usados para clasificar productos
y calcular márgenes por nivel de cliente. Se formalizan aquí con los mismos
nombres técnicos y campos que en el export de Studio, para que al
actualizar la base de datos de producción real Odoo tome las tablas ya
existentes sin perder datos.
"""

from odoo import models, fields


class XFabricante(models.Model):
    _name = 'x_fabricante'
    _description = 'Fabricante'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_margen_A = fields.Float(string='Margen A')
    x_studio_margen_B = fields.Float(string='Margen B')
    x_studio_margen_C = fields.Float(string='Margen C')
    x_studio_margen_D = fields.Float(string='Margen D')
    x_studio_margen_E = fields.Float(string='Margen E')
    x_studio_margen_F = fields.Float(string='Margen F')
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XFamilia(models.Model):
    _name = 'x_familia'
    _description = 'Familia'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XLinea(models.Model):
    _name = 'x_linea'
    _description = 'Línea'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XGrupo(models.Model):
    _name = 'x_grupo'
    _description = 'Grupo'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
