# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class AuthorizeController(http.Controller):
    _relay_url = '/payment/authorize_net/complete'
    _cancel_url = '/payment/authorize_net/cancel'
    _test_url = 'https://developer.authorize.net/tools/paramdump/index.php'

    @http.route('/payment/authorize_net/complete', type='http', auth="none", methods=['POST', 'GET'])
    def authorize_complete(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request.registry['payment.transaction'].form_feedback(cr, uid, post, 'authorize_net', context=context)
        return werkzeug.utils.redirect(post.pop('return_url', '/'))

    @http.route('/payment/authorize_net/cancel', type='http', auth="none")
    def authorize_cancel(self, **post):
        """ When the user cancels payment """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        _logger.info('Beginning Authorize.Net cancel with post data %s', pprint.pformat(post))  # debug
        return werkzeug.utils.redirect('/')