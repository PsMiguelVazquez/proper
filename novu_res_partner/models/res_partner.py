from odoo import models, fields
import io
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'


    team_id = fields.Many2one('crm.team', 'Sales Team', help='	Si se establece, este equipo de ventas se utilizará para las ventas y asignaciones relacionadas con este partner.')