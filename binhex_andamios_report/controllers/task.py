from odoo import http
from odoo.addons.project.controllers.portal import CustomerPortal

from odoo import _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.payment.controllers.portal import PaymentProcessing

import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/task/<int:task_id>/accept'], type='json', auth="public", website=True)
    def portal_task_accept(self, task_id, access_token=None, partner_name=None, signature=None):
        try:
            task_sudo = request.env['project.task'].sudo().browse(task_id)
        except (AccessError, MissingError):
            return {'error': _('Invalid task')}

        if not signature:
            return {'error': _('Signature is missing.')}

        task_sudo.signature = signature

        return {
            'task_id': task_id,
            'force_refresh': True,
            'redirect_url': task_sudo.get_portal_url(query_string='&message=sign_ok'),
        }
