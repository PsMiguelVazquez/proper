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
        try:
            product_categories = self.env['product.category'].search([])
            jsListaProductCategories = []

            for product_category in product_categories:
                jsListaProductCategories.append(self._generarDiccionarioGenerico(product_category))

            jsListaProductCategories = sorted(jsListaProductCategories, key=lambda x: x["id"])

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProductCategories)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerCategoriasPublicas(self, *args):
        try:
            product_public_categories = self.env['product.public.category'].search([])
            jsListaProductPublicCategories = []

            for product_public_category in product_public_categories:
                jsListaProductPublicCategories.append(self._generarDiccionarioGenerico(product_public_category))

            jsListaProductPublicCategories = sorted(jsListaProductPublicCategories, key=lambda x: x["id"])

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProductPublicCategories)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerProductosTiendaProper(self, *args):
        try:
            products = self.env['product.product'].search([
                            ('product_tmpl_id.sale_ok', '=', True),
                            ('product_tmpl_id.proper', '=', True)
                        ])
            jsListaProducts = []

            for product in products:
                jsListaProducts.append(self._generarDiccionarioProducto(product))

            jsListaProducts = sorted(jsListaProducts, key=lambda x: x["id"])

            return self.RespuestaWSTienda(True, 0, "exitosa", jsListaProducts)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def ObtenerImagenProducto(self, *args, **kwargs):
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
                param_name = args[0]
                return {'error': 'Parámetro mal formado'}
            if product_ids and isinstance(product_ids, list):
                product_ids = [int(pid) if isinstance(pid, str) and pid.isdigit() else pid for pid in product_ids]
                product_ids = [pid for pid in product_ids if isinstance(pid, int)]

            if product_ids:
                productos = self.env['product.product'].search([('id', 'in', product_ids)])
                jsListaImageProducts = []

                for producto in productos:
                    jsListaImageProducts.append(self._generarDiccionarioImagenProducto(producto))

                jsListaImageProducts = sorted(jsListaImageProducts, key=lambda x: x["id"])

                return self.RespuestaWSTienda(True, 0, "exitosa", jsListaImageProducts)

        except Exception as e:
            return self.RespuestaWSTienda(False, e.pgcode if hasattr(e, "pgcode") else '-1',\
                                                                            e.name if hasattr(e, "name") else str(e), '')

    def CrearOportunidad(self, *args):
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
        # MIGRACIÓN V19: `detailed_type` fue eliminado; el campo `type` de
        # `product.template` volvió a ser el único (ya no hay split
        # `type`/`detailed_type`).
        jsRespuesta = {
            'id': record.id,
            'product_tmpl_id': record.product_tmpl_id.id,
            'name': record.name,
            'type': record.type,
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
