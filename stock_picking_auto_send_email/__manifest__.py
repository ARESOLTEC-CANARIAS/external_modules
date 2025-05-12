##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2025 Aresoltec S.L. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'stock_picking_auto_send_email',
    'version': '16.0.1.1',
    'category': 'Custom',
    "license": "AGPL-3",
    'description': "Allows to send delivery notes on order completion",
    'summary': 'Allows to send delivery notes on order completion',
    "author": "Aresoltec",
    "website": "https://aresoltec.com",
    'depends': [
      'stock',
      'mail',
    ],
    'data': [
      'data/mail_template_data.xml',
      'views/res_partner_views.xml',
#        'security/ir.model.access.csv',
#        'security/sms_security.xml',
    ],
    'installable': True,
    'application': True,
}
