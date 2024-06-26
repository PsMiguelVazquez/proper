{
    'name': "Almacén de refacturación",

    'summary': """
        Almacén de refacturación""",

    'description': """
        Crea entradas/salidas automáticas al almacén de refacturación cuando se crea una nota de crédito y cuando
        se utiliza la acción Refactuación crédito
    """,
    'license': 'LGPL-3',

    'author': "Jonathan Alfaro",
    "depends": ["base","account"],
    'data': [
        'views/account_move.xml',
    ],
}