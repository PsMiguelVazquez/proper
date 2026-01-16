{
    'name': 'Novu sale_order',
    'version': '19.0.0.1',
    'category': '',
    'license': 'OPL-1',
    'summary': 'Agrega campos necesarios en la venta',

    'author': 'Mayra Carrillo',
    'maintainer': '',
    'website': '',

    'depends': ['sale', 'vehiculos', 'web_studio', 'sale_purchase_confirm','sale_stock','sale_line_date_planned','sale_management','mail'],
    'data': [
            'views/sale_order_view.xml',
            'views/sale_order_mkp.xml',
            'views/sale_order_action_mkp.xml',
            'security/sale_order_groups.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': False,
    'application': False,
    'active': False,

}
