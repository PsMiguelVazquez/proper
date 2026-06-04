# -*- coding:utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime
import logging
import traceback
from datetime import timedelta
import base64
import zipfile
import io
from lxml import etree
_logger = logging.getLogger(__name__)


class WsTienda(models.Model):
    _name = "ws.tienda"
    _description = "Web Service Tienda en linea."

    def ObtenerCategoriaProducto(self, *args):
        # _logger.error("ENTRE XD")
        try:
            product_categories = self.env['product.category'].search([])
            _logger.error(f"product_categories: {product_categories} XD")
            jsListaProductCategories = []

            for product_category in product_categories:
                jsListaProductCategories.append(self._generarDiccionarioGenerico(product_category))

            jsListaProductCategories = sorted(jsListaProductCategories, key=lambda x: x["id"])
            _logger.error(f"jsListaProductCategories: {jsListaProductCategories} XD")

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProductCategories)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerCategoriasPublicas(self, *args):
        # _logger.error("ENTRE XD")
        try:
            product_public_categories = self.env['product.public.category'].search([])
            _logger.error(f"product_public_categories: {product_public_categories} XD")
            jsListaProductPublicCategories = []

            for product_public_category in product_public_categories:
                jsListaProductPublicCategories.append(self._generarDiccionarioGenerico(product_public_category))

            jsListaProductPublicCategories = sorted(jsListaProductPublicCategories, key=lambda x: x["id"])
            _logger.error(f"jsListaProductPublicCategories: {jsListaProductPublicCategories} XD")

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProductPublicCategories)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerProductosTiendaProper(self, *args):
        _logger.error("ENTRE 2 XD")
        try:
            products = self.env['product.product'].search([
                            ('product_tmpl_id.sale_ok', '=', True),
                            ('product_tmpl_id.proper', '=', True)
                        ])
            _logger.error(f"products: {products} XD")
            jsListaProducts = []

            for product in products:
                jsListaProducts.append(self._generarDiccionarioProducto(product))

            jsListaProducts = sorted(jsListaProducts, key=lambda x: x["id"])
            _logger.error(f"jsListaProducts: {jsListaProducts} XD")

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProducts)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerImagenProducto(self, *args, **kwargs):
        _logger.error("ENTRE MBCT 2 XD")
        _logger.error(f"args: {args}")
        _logger.error(f"kwargs: {kwargs}")
        try:
            # Los parámetros pueden venir en diferentes lugares
            product_ids = None
            
            # Caso 1: Vienen en kwargs
            if kwargs:
                product_ids = kwargs.get('product_ids')
            
            # Caso 2: Vienen en args como diccionario
            if not product_ids and args and isinstance(args[0], dict):
                product_ids = args[0].get('product_ids')
            
            # Caso 3: Vienen como args planos (tu caso actual)
            if not product_ids and args and len(args) == 1 and isinstance(args[0], str):
                # args[0] es 'product_ids', pero necesitas el valor
                # Esto es un hack - mejor arreglar el wrapper
                param_name = args[0]
                # No tenemos el valor porque el wrapper lo perdió
                _logger.error(f"Error: El wrapper pasó solo el nombre '{param_name}' sin su valor")
                return {'error': 'Parámetro mal formado'}
            if product_ids and isinstance(product_ids, list):
                # Convierte strings a enteros, mantiene los que ya son enteros
                product_ids = [int(pid) if isinstance(pid, str) and pid.isdigit() else pid for pid in product_ids]
                # Filtra solo los que son enteros (por si algún string no era número)
                product_ids = [pid for pid in product_ids if isinstance(pid, int)]
            _logger.error(f"product_ids final: {product_ids}")
            
            if product_ids:
                productos = self.env['product.product'].search([('id', 'in', product_ids)])
                #_logger.error(f"products: {productos} XD")
                jsListaImageProducts = []
    
                for producto in productos:
                    jsListaImageProducts.append(self._generarDiccionarioImagenProducto(producto))
    
                jsListaImageProducts = sorted(jsListaImageProducts, key=lambda x: x["id"])
                # _logger.error(f"jsListaImageProducts: {jsListaImageProducts}")
                _logger.error(f"Finalice sincronizacion IMGs XD")
    
                return self.RespuestaWSTienda(True, 0, "exitosa", jsListaImageProducts)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def CrearOportunidad(self, *args):
        _logger.error("ENTRE Crear")
        for oportunidad in args:
            try: 
                json_oportunidad = oportunidad['infoOportunidad']
                registro_oportunidad = {
                    'name': json_oportunidad['name'],
                    'email_from': json_oportunidad['email_from'],
                    'phone': json_oportunidad['phone'],
                    'contact_name': json_oportunidad['contact_name'],
                    'source_id': json_oportunidad['source_id'],
                    'captado_en': json_oportunidad['captado_en'],
                    'mensaje': json_oportunidad['mensaje'],
                    'type': 'opportunity'
                    }
    
                oportunidad_modelo = self.env['crm.lead']
                resultado_oportunidadCreada = oportunidad_modelo.create(registro_oportunidad)
                jsListaOpertunidadCreada = []
                
                jsListaOpertunidadCreada.append(self._generarDiccionarioGenerico(resultado_oportunidadCreada))
                
                return self.RespuestaWSTienda(True, 0, "exitosa", jsListaOpertunidadCreada)
    
            except Exception as e:
                _logger.error(e)
                return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                                e.name if hasattr(e, "name") else str(e), "")
            


    def _generarDiccionarioGenerico(self, record):
        jsRespuesta = {
            'id': record.id,
            'name': record.name
        }

        return jsRespuesta

    def _generarDiccionarioProducto(self, record):
        jsRespuesta = {
            'id': record.id,
            'product_tmpl_id': record.product_tmpl_id.id,
            'name': record.name,
            'type': record.detailed_type,
            'unspsc_code_id': record.unspsc_code_id.id,
            'default_code': record.default_code,
            'categ_id': record.categ_id.id,
            'uom_id': record.uom_id.id,
            'public_categ_ids': record.public_categ_ids.ids
        }

        return jsRespuesta

    def _generarDiccionarioImagenProducto(self, record):
        jsRespuesta = {
            'id': record.id,
            'image_1920': record.image_1920
        }

        return jsRespuesta
 
        

    def RespuestaWSTienda(self, procesada, codigoError, mensaje, catalogo):
        value = {
            "procesada": procesada,
            "codigoError": codigoError,
            "descripcion": mensaje,
            "catalogo": catalogo
        }
        
        return value