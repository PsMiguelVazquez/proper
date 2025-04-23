from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
class WebsiteSalePromo(WebsiteSale):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        promo = post.get('promo')
  
        response = super().shop(page=page, category=category, search=search, ppg=ppg, **post)
        if promo:
            pricelist = request.env['product.pricelist'].sudo().search([('name', '=', 'descuentos?')], limit=1)
            if pricelist:
                request.website.pricelist_id = pricelist.id
                request.session['website_sale_current_pl'] = pricelist.id



                pricelist_items = request.env['product.pricelist.item'].sudo().search([('pricelist_id', '=', pricelist.id)])
                products = pricelist_items.mapped('product_tmpl_id')
                response.values['products'] = products
                _logger.error(products.name)
                if products:
                    # Aseguramos que los productos estén en el contexto
                    prod = request.env['product.template'].browse(214825)
                    response.values['products'] = prod
                    _logger.error(response.qcontext['products'])
                else:
                    # Si no se encuentran productos, pasamos una lista vacía o mostramos un mensaje
                    response.qcontext['products'] = []
                    response.qcontext['error_message'] = 'No products found in the "descuentos?" pricelist.'

        # Devolvemos la respuesta con los productos filtrados

        _logger.error(response)
        return response