{
    'name': "Stock Block Invoice Novu",
    'version': '15.0.1.0.0',
    'summary': 'Bloquea la facturación si no hay inventario disponible.',
    'description': """
        Módulo personalizado para Novu.
        Bloquea la creación de facturas desde órdenes de venta
        cuando los productos almacenables no tienen suficiente stock
        en el almacén de la orden.
        HU: No permitir facturar sin inventario.
    """,
    'author': "Ernesto Alfonso Sánchez Montiel",
    'website': "https://www.novu.com/",
    'category': 'Sales/Sales',
    'depends': ['sale_stock'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}