# -*- coding: utf-8 -*-
{
    'name': 'Novu Reportes de Polizas',
    'version': '0.1',
    'license': 'LGPL-3',
    'summary': 'Se agrega menu en contabilidad > reportes de polizas para descargar excel',
    'description': """
        Se agrega menu en contabilidad > reportes de polizas para descargar excel.
    """,
    'author': 'Mayra Carrillo',
    'depends': ['account'],
    'data': [
         'security/ir.model.access.csv',
         'data/secuencia_poliza_diario.xml',
         'views/reportes_polizas_wizard.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}