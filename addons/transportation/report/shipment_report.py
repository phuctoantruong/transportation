from openerp import api, models
import json

class shipment_report(models.AbstractModel):
    
    #name must be: report.module_name.template_id
    _name = "report.transportation.shipment_report_pdf"
    
    def direction(self,txt):
        j = json.loads(txt)
        return j
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('transportation.shipment_report_pdf')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'ship': self.env['shipment.management'].browse(self._ids),
            'ship_line': self.env['shipment.management.line'].search([('ship_id','=',self._ids)]),
            'direction': self.direction,
        }
        return report_obj.render('transportation.shipment_report_pdf', docargs)