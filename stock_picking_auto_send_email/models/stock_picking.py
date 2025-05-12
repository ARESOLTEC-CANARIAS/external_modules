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

from odoo import models, _

import threading


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _send_confirmation_email(self):
        super(Picking, self)._send_confirmation_email()
        if not getattr(threading.current_thread(), 'testing', False) and not self.env.registry.in_test_mode():
            pickings = self.filtered(lambda p: p.partner_id.stock_move_email_validation and p.picking_type_id.code == 'outgoing')
            for picking in pickings:
                template_id = self.env.ref('stock_picking_auto_send_email.mail_template_data_delivery_confirmation').id
                picking.with_context(force_send=True).message_post_with_template(template_id, email_layout_xmlid='mail.mail_notification_light')
