from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    es_vendedor = fields.Boolean(string="Es Vendedor", compute="_compute_es_vendedor")

    def _compute_es_vendedor(self):
        user = self.env.user
        group = self.env.ref('novu_sale_order.vendedor', raise_if_not_found=False)

        # Verifica si el grupo existe y si el usuario está en el grupo
        if group and user in group.users:
            self.es_vendedor = True
        else:
            self.es_vendedor = False


    @api.model_create_multi
    def create(self, vals_list):
        user = self.env.user
        no_puede_crear = (
                        user.has_group('novu_sale_order.vendedor')
                    )
        _logger.error('create no_puede_crear {}'.format(no_puede_crear))
        if no_puede_crear:
            raise ValidationError('No cuenta con permisos para crear o editar productos. Verifique sus permisos o póngase en contacto con su administrador.')

        return super(ProductTemplate, self).create(vals_list)
