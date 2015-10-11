# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website_sale.controllers.main import website_sale as ws
import json


class website_sale(ws):

    def get_attributes(self, product):
        attributes = []
        for a in product.attribute_line_ids:
            attributes.append([a.attribute_id.id, a.attribute_id.name, a.attribute_id.related_attribute_id.id])
        return json.dumps(attributes)

    def get_combination_values(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        currency_obj = pool['res.currency']
        attribute_combination = []

        website_currency_id = request.website.currency_id.id
        currency_id = self.get_pricelist().currency_id

        for p in product.product_variant_ids:
            comb = {}
            for av in p.attribute_value_ids:
                amount = currency_obj.compute(cr, uid, website_currency_id, currency_id.id, av.price_extra)
                comb[av.attribute_id.id] = [av.id, av.name, amount]
            attribute_combination.append(comb)
        return json.dumps(attribute_combination)

    def get_currency(self):
        currency_id = self.get_pricelist().currency_id
        return json.dumps([currency_id.symbol, currency_id.position])

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        r = super(website_sale, self).product(product, category, search, **kwargs)
        r.qcontext['get_attributes'] = self.get_attributes
        r.qcontext['get_combination_values'] = self.get_combination_values
        r.qcontext['get_currency'] = self.get_currency
        return r
