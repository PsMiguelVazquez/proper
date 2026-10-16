# -*- coding: utf-8 -*-

from odoo import fields, models


class Marketplace(models.Model):
    _name = 'novu_sale_order.marketplace'
    _description = 'Marketplace de origen (Origen MKP)'
    _order = 'name'

    # Catálogo editable por Ventas / Administrador (ver security/
    # ir.model.access.csv, y la pantalla de administración en
    # novu_sale_order: Ventas > Configuración > Marketplaces), para que
    # agregar un marketplace nuevo (p.ej. "SHOPIFY") ya no requiera tocar
    # código ni hacer un despliegue -antes era un Selection con la lista
    # fija en sale.order.x_studio_origen_mkp-.
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Ya existe un marketplace con ese nombre.'),
    ]
