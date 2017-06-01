# -*- coding: utf-8 -*-
from openerp import models, fields,api
class res_country(models.Model):
    _inherit = "res.country"
    
    city_id = fields.One2many("res.country.city","country_id",string = "City")
    
    
class res_city(models.Model):
    _name = "res.country.city"
    
    name = fields.Char("City", required=True)
    country_id = fields.Many2one("res.country","Country",required=True)
    district_id = fields.One2many("res.country.city.district","city_id",string = "District")

class res_district(models.Model):
    _name = "res.country.city.district"
    
    name = fields.Char("District", required=True)
    city_id = fields.Many2one("res.country.city","City", required=True)
    ward_id = fields.One2many("res.country.city.district.ward","district_id",string = "Ward")
    

class res_ward(models.Model):
    _name = "res.country.city.district.ward"

    name = fields.Char("Ward", required = True)
    district_id = fields.Many2one("res.country.city.district","District", required = True)
