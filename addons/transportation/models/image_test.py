# -*- coding: utf-8 -*-
from openerp import fields, models, _, api

class image_test(models.Model):
    _name = "nn.image.test"
    
    name = fields.Char("Name",required=True, translate=True)
    image = fields.Binary("Image", help="This field holds the image used as image for our customers, limited to 1024x1024px.")
    