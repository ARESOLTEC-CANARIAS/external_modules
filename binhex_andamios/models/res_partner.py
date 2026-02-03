from odoo import models, fields, _
import logging
_logger = logging.getLogger(__name__)


class andamios(models.Model):
    _inherit = 'res.partner'

    andamio_ids = fields.One2many('scaffold.scaffold', 'client_id', string='Scaffold')
    andamio_ids_size = fields.Integer(string='Scaffold Qty', compute="_andamio_id_size_update")

    def action_show_andamios_treeview(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scaffolds'),
            'view_mode': 'list',
            'res_model': 'scaffold.scaffold',
            'view_id': self.env.ref('binhex_andamios.andamios_list').id,
            'domain': [('id', 'in', (self.andamio_ids).ids)],
        }

    def _andamio_id_size_update(self):
        for record in self:
            record.andamio_ids_size = len((record.andamio_ids).ids)

    def name_get(self):
        if self.env.context.get("show_name_only"):
            return [(rec.id, rec.name) for rec in self]
        return super().name_get()
