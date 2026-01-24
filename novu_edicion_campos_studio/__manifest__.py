{
    'name': 'Novu edicion de campos studio',
    'version': '0.1',
    'category': '',
    'license': 'OPL-1',
    'summary': 'Edita campos de studio que no son necesarios e interfieren el uso correcto de flujos nativos',
    'description': """Edita campos de studio que no son necesarios e interfieren el uso correcto de flujos nativos""",

    'author': 'Mayra Carrillo',
    'maintainer': '',
    'website': '',

    'depends': ['base', 'product', 'web_studio'],
    'data': [
            
    ],
    'assets': {},
    'post_init_hook': 'odoo.addons.novu_edicion_campos_studio.hooks.post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False

}
