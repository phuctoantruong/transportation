# -*- coding: utf-8 -*-
from openerp import fields, models, _, api
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class sale_order(models.Model):
    _inherit = "sale.order"
    
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('planned', 'Planned'),
        ('in_shipment','In Shipment'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    
    #Do not create stock.picking
    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
        return True
    
    @api.multi
    def action_planned(self):
        for order in self:
            order.state = 'planned'
    
    #TODO:
    #create stock.picking       
    @api.multi
    def action_to_shipment(self, location_code=None):
        for order in self:
            #Change stock.warehouse
            if location_code:
                stock_warehouse_obj = self.env['stock.warehouse'].search([('code', '=', location_code)])
                order.warehouse_id = stock_warehouse_obj
            #end
            #Create stock.picking
            order.order_line._action_procurement_create()
#             order._create_picking()
            #end
            order.state = 'in_shipment'
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True
    
#     @api.multi
#     def _get_destination_location(self):
#         return self.picking_type_id.default_location_dest_id.id
#     
#     @api.model
#     def _prepare_picking(self):
#         return {
#             'picking_type_id': self.picking_type_id.id,
#             'partner_id': self.partner_id.id,
#             'date': self.create_date,
#             'origin': self.name,
#             'location_dest_id': self._get_destination_location,
#             'location_id': self.partner_id.property_stock_customer.id, 
#         }
#         
#     @api.multi
#     def _create_picking(self):
#         for order in self:
#             ptypes = order.order_line.mapped('product_id.type')
#             if ('product' in ptypes) or ('consu' in ptypes):
#                 res = order._prepare_picking()
#                 picking = self.env['stock.picking'].create(res)
#                 moves = order.order_line._create_stock_moves(picking)
#                 moves.action_confirm()
#                 moves.force_assign()
#         return True
#     
#     @api.multi
#     def _create_stock_moves(self, picking):
#         moves = self.env['stock.move']
#         done = self.env['stock.move'].browse()
#         for line in self:
#             order = line.order_id
#             price_unit = line.price_unit
#             if line.taxes_id:
#                 price_unit = line.taxes_id.compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
#             if line.product_uom.id != line.product_id.uom_id.id:
#                 price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
#             if order.currency_id != order.company_id.currency_id:
#                 price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
# 
#             template = {
#                 'name': line.name or '',
#                 'product_id': line.product_id.id,
#                 'product_uom': line.product_uom.id,
#                 'date': line.order_id.create_date,
#                 'date_expected': line.date_planned,
#                 'location_id': line.order_id.picking_type_id.default_location_src_id.id or line.order_id.partner_id.property_stock_customer.id,
#                 'location_dest_id': line.order_id._get_destination_location(),
#                 'picking_id': picking.id,
#                 'partner_id': line.order_id.dest_address_id.id or line.order_id.partner_id.id, 
#                 'move_dest_id': False,
#                 'state': 'draft',
#                 'purchase_line_id': line.id,
#                 'company_id': line.order_id.company_id.id,
#                 'price_unit': price_unit,
#                 'picking_type_id': line.order_id.picking_type_id.id,
#                 'group_id': line.order_id.procurement_group_id.id,
#                 'procurement_id': False,
#                 'origin': line.order_id.name,
#                 'route_ids': line.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
#                 'warehouse_id':line.order_id.picking_type_id.warehouse_id.id,
#             }
#         return done
#     
#     def _force_picking_done(self, cr, uid, picking_id, context=None):
#         context = context or {}
#         picking_obj = self.pool.get('stock.picking')
#         picking_obj.action_confirm(cr, uid, [picking_id], context=context)
#         picking_obj.force_assign(cr, uid, [picking_id], context=context)
#         # Mark pack operations as done
#         pick = picking_obj.browse(cr, uid, picking_id, context=context)
#         lot = self._create_lot(cr, uid, pick, context)
#         for pack in pick.pack_operation_ids.filtered(lambda x: x.product_id.tracking == 'none'):
#             self.pool['stock.pack.operation'].write(cr, uid, [pack.id], {'qty_done': pack.product_qty}, context=context)
#         if not any([(x.product_id.tracking != 'none') for x in pick.pack_operation_ids]):
#             picking_obj.action_done(cr, uid, [picking_id], context=context)
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order'] #Empty recordset
        for line in self:
            #change state 'sale' to 'planning'
            if line.state != 'planned' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_procs += new_proc
        new_procs.run()
        return new_procs
