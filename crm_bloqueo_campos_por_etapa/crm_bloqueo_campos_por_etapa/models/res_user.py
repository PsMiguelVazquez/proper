from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    #equipo_usuarios = fields.Many2many(comodel_name='res.users', string='Team Members')
    equipo_usuarios = fields.Many2many(
        comodel_name='res.users', relation='res_users_equipo_usuarios_rel', column1='user_id', column2='equipo_user_id', string='Usuarios del equipo')