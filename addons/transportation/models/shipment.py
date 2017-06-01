from openerp import models,fields,api
class Shipment(models.Model):
    _name = "shipment.management"
    
    name = fields.Char("Name", required=True)
    route = fields.Char("Route", required=True)
    depot_address = fields.Char("Depot Address")
    state = fields.Selection([("plan","Plan"),
                              ("ready","Ready"),
                              ("done","Done")],
                             string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='ready')
    ship_line_ids = fields.One2many("shipment.management.line","ship_id",String = "Order lines")
    
    #TODO:
    #stockpicking DONE
    @api.one
    def done_progressbar(self):
        for i in self.ship_line_ids:
            i.sale_order_id.write({'state': 'done',
                                   })
        self.write({'state': 'done',
                    })
        
class ShipmentLine(models.Model):
    _name = "shipment.management.line"
    
    name = fields.Char("Name", required=True)
    index = fields.Integer("Index", required=True)
    sale_order_id = fields.Many2one("sale.order", "Sale Order", required=True)
    order_id = fields.Integer("order_id")
    address = fields.Char("Address", required=True)
    ship_id = fields.Many2one("shipment.management",string = "Shipment Reference", ondelete='cascade', index=True, copy=False)