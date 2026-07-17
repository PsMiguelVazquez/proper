# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: `x_fabricante`, `x_familia`, `x_linea`, `x_grupo`,
`x_caracteristica_1`, `x_color`, `x_sublinea`, `x_modelo_del_producto` y
`x_numero_de_serie_arti`/`x_numero_de_serie_moto` eran modelos propios
creados enteramente con Odoo Studio en la base de datos de producción de
v15 (sin código de módulo), usados para clasificar productos y calcular
márgenes por nivel de cliente. Se formalizan aquí con los mismos nombres
técnicos y campos que en el export de Studio, para que al actualizar la
base de datos de producción real Odoo tome las tablas ya existentes sin
perder datos.
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


class XCaracteristica1(models.Model):
    _name = 'x_caracteristica_1'
    _description = 'Característica 1'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XColor(models.Model):
    _name = 'x_color'
    _description = 'Color'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XSublinea(models.Model):
    _name = 'x_sublinea'
    _description = 'Sublínea'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XModeloDelProducto(models.Model):
    _name = 'x_modelo_del_producto'
    _description = 'Modelo del producto'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XNumeroDeSerieArti(models.Model):
    _name = 'x_numero_de_serie_arti'
    _description = 'Numero de serie articulo'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XNumeroDeSerieMoto(models.Model):
    _name = 'x_numero_de_serie_moto'
    _description = 'Número de serie Motor'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
