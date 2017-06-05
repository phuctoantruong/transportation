# -*- coding: utf-8 -*-
{
    'name': 'General Sale',
    'description': '',
    'author': '',   
    'application': True,
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_view.xml'
    ],
}
