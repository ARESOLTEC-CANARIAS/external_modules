
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ScaffoldZone(models.Model):
    _name = 'scaffold.zone'
    _order = "sequence, name, id"

    sequence = fields.Integer(string="Sequence", default=1)
    name = fields.Char(string="Name", required=True)
