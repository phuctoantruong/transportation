# -*- coding: utf-8 -*-
{
    'name': 'transportation',
    'description': 'shipment',
    'author': 'NN',   
    'application': True,
    'depends':['base','sale','stock'],
    'data': [
             "views/shipment_view.xml",
             "views/res_partner_view.xml",
             "views/admin_view.xml",
             "views/sale_order_view.xml",
             "views/stock_picking_view.xml",
             "views/image_test_view.xml",
             "report/shipment_report_pdf.xml",
             "report/report_view.xml"
    ]
}