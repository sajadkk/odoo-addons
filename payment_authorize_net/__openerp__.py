# -*- coding: utf-8 -*-
##############################################################################
# Sajad KK <kksajad@gmail.com>
# Copyright (c) 2015, Sajad KK
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program;
# If not, see <http://www.gnu.org/licenses/> or  write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{
    'name': 'Authorize.net Payment Acquirer',
    'category': 'Payment',
    'summary': 'Payment Acquirer: Authorize.net Implementation',
    'version': '1.0',
    'description': """Authorize.net Payment Acquirer""",
    'author': 'Sajad KK',
    'depends': ['payment'],
    'data': [
        'views/authorize.xml',
        'views/payment_acquire.xml',
        'data/authorize.xml'
    ],
    'installable': True,
}
