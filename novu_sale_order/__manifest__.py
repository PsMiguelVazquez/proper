{
    'name': 'Novu sale_order',
    'version': '19.0.0.6',
    'category': '',
    'license': 'OPL-1',
    'summary': 'Agrega campos necesarios en la venta',

    'author': 'Mayra Carrillo',
    'maintainer': '',
    'website': '',

    # MIGRACIÓN V19: se agrega `studio_fields_v19`, que define
    # `x_sale_id_stock_picking_count`, `x_comision`, `x_utilidad` y
    # `x_utilidad_total` (usados en las vistas de este módulo).
    # También se agrega `sale_order_utilities`, que define
    # `sale.order.line.x_obse_comprador` (usado en `views/sale_order_view.xml`);
    # sin esta dependencia explícita, el orden de carga entre ambos módulos
    # no está garantizado y falla con 'El campo "x_obse_comprador" no
    # existe en el modelo "sale.order.line"' si `sale_order_utilities`
    # todavía no había registrado ese campo en este rebuild del registro.
    'depends': ['sale', 'vehiculos', 'web_studio', 'sale_purchase_confirm','sale_stock','sale_line_date_planned','sale_management','mail', 'account','base', 'studio_fields_v19', 'sale_order_utilities'],
    'pre_init_hook': 'pre_init_hook',
    'data': [
            'security/ir.model.access.csv',
            'views/x_wizard_rechcoti_view.xml',
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
