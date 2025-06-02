from odoo import models, fields, api

class CycleTypeTermo(models.Model):
    _inherit = 'afr.cycle.type'

    is_termodesifectora = fields.Boolean('É termodesinfectora', default=False)
   