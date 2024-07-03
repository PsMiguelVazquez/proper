# -*- coding: utf-8 -*-
{
    'name': "upload_invoice_sales",

    'summary': """
        Permite subir una adjuntos y asignarla a ordenes de venta""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale','account','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/upload_invoice_view.xml',
        'views/views.xml'
        #'views/templates.xml',
    ],

}
