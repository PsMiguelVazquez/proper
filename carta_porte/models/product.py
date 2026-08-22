from odoo import fields, models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # MIGRACIÓN V19: esta constraint (`unique(default_code)`) existía en el
    # código de 15.0 como `_sql_constraints`, pero en producción hay ~30
    # grupos de productos con `default_code` duplicado -la gran mayoría con
    # dos productos ACTIVOS compartiendo el mismo código (ver ejemplo
    # "WR-810 UHF")-, así que el índice único nunca llegó a crearse
    # realmente ahí tampoco: sólo generaba un WARNING silencioso en cada
    # arranque, sin bloquear nada. Se elimina la declaración -en vez de
    # dejarla fallando- para no seguir marcando la rama en Odoo.sh como
    # "Warning" por un dato que requiere que el negocio decida, producto
    # por producto, cuál código es el correcto, no un fix automático.
