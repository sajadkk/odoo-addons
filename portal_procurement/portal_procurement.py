# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class ProcurementOrder(osv.Model):
    _inherit = "procurement.order"

    def create(self, cr, user, vals, context=None):
        if context is None:
            context = {}
        if context.get('portal'):
            vals['state'] = 'draft'
        return super(ProcurementOrder, self).create(cr, user, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        procurements = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in procurements:
            if s['state'] in ['cancel', 'draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'),
                        _('Cannot delete Procurement Order(s) which are in %s state.') % s['state'])
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

    def _get_default_partner_id(self, cr, uid, context=None):
        """ Gives default partner_id """
        if context is None:
            context = {}
        if context.get('portal'):
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            # Special case for portal users, as they are not allowed to call name_get on res.partner
            # We save this call for the web client by returning it in default get
            return self.pool['res.partner'].name_get(cr, SUPERUSER_ID, [user.partner_id.id], context=context)[0]
        return False

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, readonly=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, readonly=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, readonly=True),

        'product_uos_qty': fields.float('UoS Quantity', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, readonly=True),
        'product_uos': fields.many2one('product.uom', 'Product UoS', states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}, readonly=True),
        'partner_id': fields.many2one('res.partner'),
        'state': fields.selection([
            ('cancel', 'Cancelled'),
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('exception', 'Exception'),
            ('running', 'Running'),
            ('done', 'Done')
        ], 'Status', required=True, track_visibility='onchange', copy=False),
    }

    _defaults = {
        'partner_id': lambda self, cr, uid, context: self._get_default_partner_id(cr, uid, context),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(ProcurementOrder, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                                    context=context, toolbar=toolbar, submenu=submenu)
        if toolbar and context.get('portal'):
            print res['toolbar']['action']
            res['toolbar']['action'] = []

        return res

    def button_confirm_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True
