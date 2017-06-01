#import openerp.addons.website_sale.controllers.main.website_sale as website_sale
from openerp.addons.website_sale.controllers.main import website_sale

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import logging
import json

class website_sale_custom(website_sale):
    
    def checkout_values(self, data=None):
        res = super(website_sale_custom, self).checkout_values(data)
        
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        
        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        orm_country = registry.get('res.country')
        state_orm = registry.get('res.country.state')
        city_orm = registry.get('res.country.city')
        district_orm = registry.get('res.country.city.district')
        ward_orm = registry.get('res.country.city.district.ward')
        
        partner = orm_user.browse(cr, SUPERUSER_ID, request.uid, context).partner_id
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        states_ids = state_orm.search(cr, SUPERUSER_ID, [], context=context)
        states = state_orm.browse(cr, SUPERUSER_ID, states_ids, context)
        
        
        order = None

        shipping_id = data and data.get('shipping_id') or None
        shipping_ids = []
        checkout = {}
        if not data:
            if request.uid != request.website.user_id.id:
                checkout.update( self.checkout_parse("billing", partner) )
                shipping_ids = orm_partner.search(cr, SUPERUSER_ID, [("parent_id", "=", partner.id), ('type', "=", 'delivery')], context=context)
            else:
                order = request.website.sale_get_order(force_create=1, context=context)
                if order.partner_id:
                    domain = [("partner_id", "=", order.partner_id.id)]
                    user_ids = request.registry['res.users'].search(cr, SUPERUSER_ID, domain, context=dict(context or {}, active_test=False))
                    if not user_ids or request.website.user_id.id not in user_ids:
                        checkout.update( self.checkout_parse("billing", order.partner_id) )
        else:
            checkout = self.checkout_parse('billing', data)
            try:
                shipping_id = int(shipping_id)
            except (ValueError, TypeError):
                pass
            if shipping_id == -1:
                checkout.update(self.checkout_parse('shipping', data))

        if shipping_id is None:
            if not order:
                order = request.website.sale_get_order(context=context)
            if order and order.partner_shipping_id:
                shipping_id = order.partner_shipping_id.id

        shipping_ids = list(set(shipping_ids) - set([partner.id]))

        if shipping_id == partner.id:
            shipping_id = 0
        elif shipping_id > 0 and shipping_id not in shipping_ids:
            shipping_ids.append(shipping_id)
        elif shipping_id is None and shipping_ids:
            shipping_id = shipping_ids[0]
            
        ctx = dict(context, show_address=1)
        shippings = []
        if shipping_ids:
            shippings = shipping_ids and orm_partner.browse(cr, SUPERUSER_ID, list(shipping_ids), ctx) or []
        if shipping_id > 0:
            shipping = orm_partner.browse(cr, SUPERUSER_ID, shipping_id, ctx)
            checkout.update( self.checkout_parse("shipping", shipping) )

        checkout['shipping_id'] = shipping_id
        
         # Default search by user country
        if not checkout.get('country_id'):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                country_ids = request.registry.get('res.country').search(cr, uid, [('code', '=', country_code)], context=context)
                if country_ids:
                    checkout['country_id'] = country_ids[0]
        ward_ids = []
        wards = {}
        district_ids = []
        districts = {}
        city_ids = []
        cities = {}
        if checkout.get("country_id"):
            city_ids = city_orm.search(cr, SUPERUSER_ID, [("country_id","=",checkout.get('country_id'))], context=context)
            cities = city_orm.browse(cr, SUPERUSER_ID, city_ids, context=context)
        if checkout.get('city_id'):
            district_ids = district_orm.search(cr, SUPERUSER_ID, [("city_id","=",checkout.get('city_id'))], context=context)
            districts = district_orm.browse(cr, SUPERUSER_ID, district_ids, context=context)
        if checkout.get('district_id'):
            ward_ids = ward_orm.search(cr, SUPERUSER_ID, [("district_id","=",checkout.get('district_id'))], context=context)
            wards = ward_orm.browse(cr,SUPERUSER_ID, ward_ids, context=context)
        
        values = {
            'countries': countries,
            'states': states,
            'cities': cities,
            'districts': districts,
            'wards': wards,
            'checkout': checkout,
            'shipping_id': partner.id != shipping_id and shipping_id or 0,
            'shippings': shippings,
            'error': {},
            'has_check_vat': hasattr(registry['res.partner'], 'check_vat'),
            'only_services': order and order.only_services or False
        }
        
        return values
    
    def _get_mandatory_billing_fields(self):
        return ["name", "phone", "email", "street", "city_id","district_id","ward_id", "country_id"]

    def _get_optional_billing_fields(self):
        return ["street2","state_id", "vat", "zip"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "phone", "street", "city_id","district_id","ward_id", "country_id"]

    def _get_optional_shipping_fields(self):
        return ["state_id", "zip"]
    
    def checkout_parse(self, address_type, data, remove_prefix=False):
        res = super(website_sale_custom, self).checkout_parse(address_type,data)
        assert address_type in ('billing', 'shipping')
        if address_type == 'billing':
            all_fields = self._get_mandatory_billing_fields() + self._get_optional_billing_fields()
            prefix = ''
        else:
            all_fields = self._get_mandatory_shipping_fields() + self._get_optional_shipping_fields()
            prefix = 'shipping_'

        # set data
        if isinstance(data, dict):
            query = dict((prefix + field_name, data[prefix + field_name])
                for field_name in all_fields if prefix + field_name in data)
        else:
            query = dict((prefix + field_name, getattr(data, field_name))
                for field_name in all_fields if getattr(data, field_name))
            if address_type == 'billing' and data.parent_id:
                query[prefix + 'street'] = data.parent_id.name

        if query.get(prefix + 'state_id'):
            query[prefix + 'state_id'] = int(query[prefix + 'state_id'])
        if query.get(prefix + 'country_id'):
            query[prefix + 'country_id'] = int(query[prefix + 'country_id'])
        if query.get(prefix + 'city_id'):
            query[prefix + 'city_id'] = int(query[prefix + 'city_id'])
        if query.get(prefix + 'district_id'):
            query[prefix + 'district_id'] = int(query[prefix + 'district_id'])
        if query.get(prefix + 'ward_id'):
            query[prefix + 'ward_id'] = int(query[prefix + 'ward_id'])

        query = self._post_prepare_query(query, data, address_type)

        if not remove_prefix:
            return query

        return dict((field_name, data[prefix + field_name]) for field_name in all_fields if prefix + field_name in data)
    def checkout_form_validate(self, data):
        res = super(website_sale_custom, self).checkout_form_validate(data)
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        error = dict()
        error_message = []

        # Validation
        for field_name in self._get_mandatory_billing_fields():
            if not data.get(field_name):
                logging.error(field_name)
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        if data.get("vat") and hasattr(registry["res.partner"], "check_vat"):
            if request.website.company_id.vat_check_vies:
                # force full VIES online check
                check_func = registry["res.partner"].vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = registry["res.partner"].simple_vat_check
            vat_country, vat_number = registry["res.partner"]._split_vat(data.get("vat"))
            if not check_func(cr, uid, vat_country, vat_number, context=None): # simple_vat_check
                error["vat"] = 'error'

        if data.get("shipping_id") == -1:
            for field_name in self._get_mandatory_shipping_fields():
                field_name = 'shipping_' + field_name
                if not data.get(field_name):
                    error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message
    @http.route('/shop/checkout/changeCity',type='http',auth='public',methods=['GET'],website=True,)
    def change_city(self, **kwargs):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result = []
        city_id = kwargs.get("city_id","")
        fields = ["id","name"]
        if city_id != "":
            res_ids = registry.get("res.country.city.district").search(cr,SUPERUSER_ID,[("city_id","=",int(city_id))],context=context)
            res = registry.get("res.country.city.district").browse(cr,SUPERUSER_ID,res_ids,context=context)
            for res_id in res:
                result.append({
                               k: getattr(res_id,k) for k in fields
                               })
            return json.dumps(result)
    @http.route('/shop/checkout/changeDistrict',type='http',auth='public',methods=['GET'],website=True,)
    def change_district(self, **kwargs):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result = []
        district_id = kwargs.get("district_id","")
        fields = ["id","name"]
        if district_id != "":
            res_ids = registry.get("res.country.city.district.ward").search(cr,SUPERUSER_ID,[("district_id","=",int(district_id))],context=context)
            res = registry.get("res.country.city.district.ward").browse(cr,SUPERUSER_ID,res_ids,context=context)
            for res_id in res:
                result.append({
                               k: getattr(res_id,k) for k in fields
                               })
            return json.dumps(result)
    @http.route('/shop/checkout/changeCountry',type='http',auth='public',methods=['GET'],website=True,)
    def change_country(self, **kwargs):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result = []
        country_id = kwargs.get("country_id","")
        fields = ["id","name"]
        if country_id != "":
            res_ids = registry.get("res.country.city").search(cr,SUPERUSER_ID,[("country_id","=",int(country_id))],context=context)
            res = registry.get("res.country.city").browse(cr,SUPERUSER_ID,res_ids,context=context)
            for res_id in res:
                result.append({
                               k: getattr(res_id,k) for k in fields
                               })
            return json.dumps(result)
        