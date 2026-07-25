{
    'name': 'Novu Purchase Order',
    'version': '19.0.0.3',
    'category': '',
    'license': 'OPL-1',
    'summary': 'Agrega campos y cambios necesarios al modulo de compras',

    'author': 'Mayra Carrillo',
    'maintainer': '',
    'website': '',

    # MIGRACIÓN V19: `views/purchase_order.xml` usa
    # `x_studio_nmero_de_factura` (formalizado en `studio_fields_v19`, no
    # es un campo del core); sin esta dependencia explícita, el orden de
    # carga entre módulos no está garantizado y falla con 'Field
    # "x_studio_nmero_de_factura" does not exist in model "purchase.order"'
    # si `studio_fields_v19` todavía no se había cargado en ese rebuild.
    'depends': ['purchase', 'web_studio', 'sale_purchase_confirm', 'studio_fields_v19'],
    'data': [
            'views/purchase_order.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': True,
    'application': False,
    'active': False,

}
