{
    "name": "carta porte",
    "summary": "",
    "author": "Cesar Lopez R",
    "version": "19.0.1.0.2",
    "license": "LGPL-3",
    # MIGRACIÓN V19: la vista usa `fecha_recepcion_cliente`, un campo real
    # definido por `costo_promedio_proper` (no por `stock`), añadido aquí
    # como dependencia explícita. Su instalación+pruebas quedan diferidas
    # hasta que `sale_purchase_confirm` (Lote 3, dependencia transitiva de
    # `costo_promedio_proper`) esté migrado.
    "depends": ['account', 'stock', 'l10n_mx_edi_stock', 'account_accountant', 'costo_promedio_proper'],
    'data': ['views/carta_porte.xml'],
}
