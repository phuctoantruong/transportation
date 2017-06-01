# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, tools
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import osv
from asyncore import write
from openerp.exceptions import ValidationError
from openerp.exceptions import  Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def default_get(self, fields):
        res_partner = self.env["res.users"].browse(self.env.user.id)
        res = super(SaleOrder, self).default_get(fields)
        if res_partner.partner_id:
            res['partner_id'] = res_partner.partner_id.id
        return res