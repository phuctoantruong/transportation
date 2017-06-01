# -*- coding: utf-8 -*-
from openerp import fields, models, _, api



class res_partner(models.Model):
    _inherit = 'res.partner'
    
    
    city_id = fields.Many2one("res.country.city",string = "City",ondelete='restrict')
    district_id = fields.Many2one("res.country.city.district",string = "District",ondelete='restrict', domain = "[('city_id','=',city_id)]")
    ward_id = fields.Many2one("res.country.city.district.ward",string = "Ward",ondelete='restrict', domain = "[('district_id','=',district_id)]")
    
    @api.multi
    def onchange_city(self, city_id):
        if city_id:
            city = self.env['res.country.city'].browse(city_id)
            return {'value': {'country_id': city.country_id.id}}
        return {'value': {}}
    @api.multi
    def onchange_district(self, district_id):
        if district_id:
            district = self.env['res.country.city.district'].browse(district_id)
            return {'value': {'city_id': district.city_id.id}}
        return {'value': {}}
    @api.multi
    def onchange_ward(self, ward_id):
        if ward_id:
            ward = self.env['res.country.city.district.ward'].browse(ward_id)
            return {'value': {'district_id': ward.district_id.id}}
        return {'value': {}}