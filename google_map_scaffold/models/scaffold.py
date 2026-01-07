from odoo import fields, models, api


class ScaffoldScaffold(models.Model):
    _inherit = "scaffold.scaffold"

    street = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    scaffold_latitude = fields.Float(string="Latitude", digits=(10, 7), default=28.4638304)
    scaffold_longitude = fields.Float(string="Longitude", digits=(10, 7), default=-16.3061883)

    def action_open_google_map(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'scaffold.scaffold',
            'res_id': self.id,
            'view_mode': 'google_map',
            'domain': [('id', '=', self.id)],
            'target': 'new',
        }

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        for scaffold in self.with_context(lang='en_US'):
            result = self._geo_localize(scaffold.street,
                                        scaffold.zip,
                                        scaffold.city,
                                        scaffold.state_id.name,
                                        scaffold.country_id.name)

            if result:
                scaffold.write({
                    'scaffold_latitude': result[0],
                    'scaffold_longitude': result[1],
                })
        return True
