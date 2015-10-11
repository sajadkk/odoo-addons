# -*- coding: utf-'8' "-*-"

import base64

try:
    import simplejson as json
except ImportError:
    import json
import hmac
import hashlib
import urlparse
import logging
import time

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_authorize_net.controllers.main import AuthorizeController
from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class AcquirerAuthorize(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_authorize_urls(self, cr, uid, environment, context=None):
        if environment == 'prod':
            return {
                'authorize_form_url': 'https://secure.authorize.net/gateway/transact.dll',
            }
        else:
            return {
                'authorize_form_url': 'https://test.authorize.net/gateway/transact.dll',
            }

    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerAuthorize, self)._get_providers(cr, uid, context=context)
        providers.append(['authorize_net', 'Authorize.net'])
        return providers

    _columns = {
        'authorize_loginid': fields.char('API User ID', required_if_provider='authorize_net'),
        'authorize_transkey': fields.char('Transaction Key', required_if_provider='authorize_net'),
        'authorize_md5hash': fields.char('MD5-HASH', required_if_provider='authorize_net',
                                         help="MD5 Hash for the transaction responses")
    }

    def authorize_net_get_form_action_url(self, cr, uid, id, context=None):
        acquirer = self.browse(cr, uid, id, context=context)
        return self._get_authorize_urls(cr, uid, acquirer.environment, context=context)['authorize_form_url']

    def _authorize_generate_fingerprint(self, acquirer, tx_type, values):
        """ Generate the fingerprint for communications.

        :param browse acquirer: the payment.acquirer browse record. It should
                                have a Transaction key
        :param dict values: transaction values

        :return string: fingerprint
        """
        assert tx_type in ('in', 'out')
        assert acquirer.provider == 'authorize_net'

        def get_value(key):
            if values.get(key):
                return values[key]
            return ''

        if tx_type == 'out':
            keys = "x_login x_invoice_num x_fp_timestamp x_amount x_currency_code".split()
            sign = '^'.join('%s' % get_value(k) for k in keys).encode('ascii')
            key = acquirer.authorize_transkey.encode('ascii')
            return hmac.new(key, sign).hexdigest()
        else:
            keys = 'md5_hash x_login x_trans_id x_amount'.split()
            sign = ''.join('%s' % get_value(k) for k in keys)
            return hashlib.md5(sign).hexdigest()

    def authorize_net_compute_fees(self, cr, uid, id, amount, currency_id, country_id, context=None):
        """ Compute fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        acquirer = self.browse(cr, uid, id, context=context)
        if not acquirer.fees_active:
            return 0.0
        country = self.pool['res.country'].browse(cr, uid, country_id, context=context)
        if country and acquirer.company_id.country_id.id == country.id:
            percentage = acquirer.fees_dom_var
            fixed = acquirer.fees_dom_fixed
        else:
            percentage = acquirer.fees_int_var
            fixed = acquirer.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def authorize_net_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)

        authorize_tx_values = dict(tx_values)
        authorize_tx_values.update({
            'x_version': '3.1',
            'x_login': acquirer.authorize_loginid,
            'x_invoice_num': tx_values['reference'],
            'x_amount': tx_values['amount'],
            'x_method': 'CC',
            'x_show_form': 'PAYMENT_FORM',
            'x_currency_code': tx_values['currency'] and tx_values['currency'].name or '',
            'x_first_name': partner_values['first_name'],
            'x_last_name': partner_values['last_name'],
            'x_address': partner_values['address'],
            'x_city': partner_values['city'],
            'x_state': partner_values['state'] and partner_values['state'].name or '',
            'x_zip': partner_values['zip'],
            'x_country': partner_values['country'] and partner_values['country'].name or '',
            'x_phone': partner_values['phone'],
            'x_email': partner_values['email'],
            'x_fp_timestamp': int(time.time()),
            'x_relay_response': 'True',
            'x_relay_url': '%s' % urlparse.urljoin(base_url, AuthorizeController._relay_url)

        })
        authorize_tx_values['x_fp_hash'] = self._authorize_generate_fingerprint(acquirer, 'out', authorize_tx_values)
        if acquirer.fees_active:
            authorize_tx_values['x_duty'] = '%.2f' % authorize_tx_values.pop('fees', 0.0)
        return partner_values, authorize_tx_values


class TxAuthorize(osv.Model):
    _inherit = 'payment.transaction'

    _columns = {
        'authorize_transid': fields.char('Transaction ID'),
        'authorize_authcode': fields.char('Authorization Code'),
        'authorize_account_number': fields.char('Account Number'),
        'authorize_paymethod': fields.char('Payment Method')

    }

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def _authorize_net_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, trans_id, tx_md5_hash = data.get('x_invoice_num'), data.get('x_trans_id'), data.get('x_MD5_Hash')
        if not reference or not trans_id or not tx_md5_hash:
            error_msg = 'Authorize.Net: received data with missing reference (%s) or trans_id (%s) or tx_md5_hash (%s)' % \
                        (reference, trans_id, tx_md5_hash)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use trans_id ?
        tx_ids = self.search(cr, uid, [('reference', '=', reference)], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'Authorize.Net: received data for reference %s' % reference
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.pool['payment.transaction'].browse(cr, uid, tx_ids[0], context=context)

        # verify fingerprint
        hash_values = {
            'md5_hash': tx.acquirer_id.authorize_md5hash,
            'x_login': tx.acquirer_id.authorize_loginid,
            'x_trans_id': trans_id,
            'x_amount': data.get('x_amount')
        }
        md5_hash = self.pool['payment.acquirer']._authorize_generate_fingerprint(tx.acquirer_id, 'in', hash_values)
        if md5_hash.upper() != tx_md5_hash.upper():
            error_msg = 'Authorize.Net: invalid fingerprint, received %s, computed %s, for data %s' % (
                tx_md5_hash, md5_hash, data)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _authorize_net_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        if data.get('x_test_request', False):
            _logger.warning(
                'Received a test transaction from Authorize.Net using sandbox'
            )

        if tx.acquirer_reference and data.get('x_trans_id') != tx.acquirer_reference:
            invalid_parameters.append(('x_trans_id', data.get('x_trans_id'), tx.acquirer_reference))
        # check what bought
        if float_compare(float(data.get('x_amount', '0.0')), tx.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('x_amount'), '%.2f' % tx.amount))

        return invalid_parameters

    def _authorize_net_form_validate(self, cr, uid, tx, data, context=None):
        if tx.state == 'done':
            _logger.warning('Authorize.Net: trying to validate an already validated tx (ref %s)' % tx.reference)
            return True

        status = int(data.get('x_response_code'))

        tx_values = {
            'acquirer_reference': data.get('x_trans_id'),
            'authorize_transid': data.get('x_trans_id'),
            'authorize_account_number': data.get('x_account_number'),
            'authorize_paymethod': data.get('x_card_type'),
            'state_message': data.get('x_response_reason_text')
        }

        if status == 1:
            _logger.info('Validated Authorize.Net payment for tx %s: set as done' % tx.reference)
            tx_values.update({
                'state': 'done',
                'authorize_authcode': data.get('x_auth_code'),
                'date_validate': fields.datetime.now(),
            })
            tx.write(tx_values)
        elif status == 4:
            _logger.info('Received notification for Authorize.Net payment %s: set as pending' % tx.reference)
            tx_values.update({'state': 'pending'})
            tx.write(tx_values)
        elif status == 2:
            _logger.info('Received notification for Authorize.Net payment %s: set as canceled' % tx.reference)
            tx_values.update({'state': 'cancel'})
            tx.write(tx_values)
        else:
            _logger.info('Received notification for Authorize.Net payment %s: set as error' % tx.reference)
            tx_values.update({'state': 'error'})
            tx.write(tx_values)


    # --------------------------------------------------
    # SERVER2SERVER RELATED METHODS
    # --------------------------------------------------

    def _authorize_net_s2s_send(self, cr, uid, values, cc_values, context=None):
        """ Create and send server-to-server transaction. """
        pass

    def _authorize_net_s2s_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        pass

    def _authorize_net_s2s_validate(self, cr, uid, tx, data, context=None):
        """ Handle the feedback of a server-to-server transaction. """
        pass

    def _authorize_net_s2s_get_tx_status(self, cr, uid, tx_id, context=None):
        """ Get the tx status. """
        pass

    def _authorize_net_form_feedback(self, cr, uid, data, acquirer_name, context=None):
        pass