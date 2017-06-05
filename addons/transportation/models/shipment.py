from openerp import models,fields,api,_
class Shipment(models.Model):
    _name = "shipment.management"
    
    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    vehicle = fields.Char("Vehicle")
    route = fields.Char("Route", required=True)
    state = fields.Selection([("plan","Plan"),
                              ("ready","Ready"),
                              ("done","Done")],
                             string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='plan')
    ship_line_ids = fields.One2many("shipment.management.line","ship_id",String = "Order lines")
    total_qty = fields.Float("Total quantity")
    maps = fields.Binary("Map")
    driving_direction = fields.Char("Direction")
    distance = fields.Float("Distance")
    duration = fields.Float("Duration")
    location_code = fields.Char("Warehouse Code", required=True)
    
    #TODO:
    #create stock picking
    @api.one
    def ready_progressbar(self):
        ship = self.env['shipment.management'].browse(self.id)
        location_code = ship.location_code
        for i in self.ship_line_ids:
            i.sale_order_id.action_to_shipment(location_code)
        self.write({'state': 'ready',
                    })
    #TODO:
    #stockpicking DONE
    @api.one
    def done_progressbar(self):
        for i in self.ship_line_ids:
            picking = self.env['stock.picking'].search([('origin','=',i.sale_order_id.name)])
            
            picking.action_done()
            
            i.sale_order_id.write({'state': 'done',
                                   })
        self.write({'state': 'done',
                    })
        
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('shipment.management') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('shipment.management') or _('New')
        for order in self.ship_line_ids.sale_order_id:
            order.action_planned()
        result = super(Shipment, self).create(vals)
        return result
    
    
class ShipmentLine(models.Model):
    _name = "shipment.management.line"
    
    name = fields.Char("Name")
    sale_order_id = fields.Many2one("sale.order", "Sale Order", required=True)
    address = fields.Char("Address", required=True)
    ship_id = fields.Many2one("shipment.management",string = "Shipment Reference", ondelete='cascade', index=True, copy=False)
    order_qty = fields.Float("Demand")
    index = fields.Integer("Index", required=True)
    
    
    