from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    field = env['ir.model.fields'].search([
        ('name', '=', 'x_studio_related_field_HW6gD'),
        ('model', '=', 'product.product'),
    ])

    if field:
        _logger.warning(
            f"Eliminando campo Studio: {field.name} ({field.model})"
        )
        field.unlink()