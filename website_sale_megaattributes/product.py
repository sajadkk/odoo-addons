# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _


class product_attribute(osv.osv):
    _inherit = "product.attribute"
    _columns = {
        'related_attribute_id': fields.many2one('product.attribute', 'Related Attribute',
                                             help=_("If given, the value of this attribute will be reloaded when the related attribute is changed.")),
    }