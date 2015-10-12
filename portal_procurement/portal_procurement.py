# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class ProcurementOrder(osv.Model):
    _inherit = "procurement.order"

    def _get_default_partner_id(self, cr, uid, context=None):
        """ Gives default partner_id """
        if context is None:
            context = {}
        if context.get('portal'):
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            return user.partner_id.id
        return False

    _columns = {
        'partner_id': fields.many2one('res.partner')
    }

    _defaults = {
        'partner_id': lambda self, cr, uid, context: self._get_default_partner_id(cr, uid, context),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(ProcurementOrder, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                                    context=context, toolbar=toolbar, submenu=submenu)
        if toolbar and context.get('portal'):
            res['toolbar']['action'] = []

        return res