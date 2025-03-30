{
    'name': 'Recepción de Residuos',
    'version': '1.0',
    'summary': 'Gestión de recepción de residuos peligrosos desde órdenes de venta',
    'category': 'Inventory',
    'author': 'Alphaqueb Consulting',
    'depends': ['sale', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/secuencia_recepcion.xml',
        'views/recepcion_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
