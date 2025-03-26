##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2022 Comunitea Servicios Tecnológicos S.L. All Rights Reserved
#    Vicente Ángel Gutiérrez Fernández <vicente@comunitea.com>
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
    'name': 'helpdesk_portal_access',
    'version': '18.0.1.0',
    'category': 'Custom',
    "license": "AGPL-3",
    'description': """
      Allows to hide everything in portal except helpdesk tickets
    """,
    'summary': 'Allows to hide everything in portal except helpdesk ticketss',
    "author": "Comunitea",
    "website": "https://comunitea.com",
    'depends': [
      'portal',
      'helpdesk_mgmt'
    ],
    'data': [
      'views/res_partner_views.xml',
      'views/portal_templates.xml',
    ],
    'installable': True,
    'application': True,
}
