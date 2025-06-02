from odoo import models, fields, api

class SupervisorioCiclosVapor(models.Model):
    _inherit = 'afr.supervisorio.ciclos'

    termo_details = fields.Many2one('afr.supervisorio.ciclos.termo.detalhes', string='Detalhes do Ciclo')
    termo_temperature = fields.Float('Temperatura de Esterilização (°C)',
    related='termo_details.termo_temperature',
    help='Temperatura alvo para esterilização')
   
    termo_phases = fields.Integer('Número de Fases ',
    related='termo_details.termo_phases',
    help='Número de fases de vácuo do ciclo')
    
    termo_drying_time = fields.Float('Tempo de Secagem (min)',
    related='termo_details.termo_drying_time',
    help='Duração da fase de secagem')
    
 
class SupervisorioCiclosVaporDetalhes(models.Model):
    _name = 'afr.supervisorio.ciclos.termo.detalhes'
    _description = 'Detalhes do Ciclo de Termodesinfecção'

   
    termo_temperature = fields.Float('Temperatura de Esterilização (°C)', help='Temperatura alvo para esterilização')
   
    termo_phases = fields.Integer('Número de Fases de Vácuo', help='Número de fases de vácuo do ciclo')
    termo_drying_time = fields.Float('Tempo de Secagem (min)', help='Duração da fase de secagem') 
    