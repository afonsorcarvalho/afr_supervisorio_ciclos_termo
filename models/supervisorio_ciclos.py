from odoo import models, fields, api
import logging
from datetime import datetime, timedelta, time
_logger = logging.getLogger(__name__)

class SupervisorioCiclosTermo(models.Model):
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

    
    @api.model
    def process_cycle_data_termo_v1(self,header,body,values):
        """
        Cria ou atualiza os dados do ciclo de ETO a partir do cabeçalho e corpo recebidos.
        
        Este método é chamado dinamicamente pelo método create_new_cycle da classe SupervisorioCiclos,
        que por sua vez é chamado pelo método action_ler_diretorio_ciclos.
        
        Args:
            header (dict): Dicionário com parâmetros do cabeçalho do ciclo
                Exemplo: {
                    'Data:': '13-4-2024',
                    'Hora:': '17:21:17', 
                    'Equipamento:': 'ETO01',
                    'Operador:': 'FLAVIOR',
                    'Cod. ciclo:': '7819',
                    'Ciclo Selecionado:': 'CICLO 01'
                }
            body (dict): Dicionário com dados do corpo do ciclo
            values (dict): Valores iniciais a serem mesclados
            create (bool): Se True, cria novo ciclo. Se False, atualiza existente
            id_ciclo (int): ID do ciclo para atualização (necessário se create=False)
            
        Returns:
            record: Registro do ciclo criado/atualizado
            
        Raises:
            UserError: Se id_ciclo não informado ao tentar atualizar
        """

        # self.ensure_one()

        _logger.debug(f"Header do ciclo: {header}")


        # procurando o ciclo selecionado no dicionário header
        ciclo_selecionado = header['CICLO']
        cycle_type = self.cycle_type_id or self.equipment_id.cycle_type_id
        cycle_features_id = cycle_type.cycle_features_id.filtered(lambda x: x.name == ciclo_selecionado)

      
      
        hora_str = header['Hora:']
        data_obj = header['Data:']
        # Extraindo horas, minutos e segundos da string de hora
        data_completa = self.data_hora_to_datetime(data_obj,hora_str)
       

        
        novos_valores = {
            'name': header['file_name'],
            'start_date': data_completa,  # Remove timezone antes de salvar
            'batch_number': header['NUMERO LOTE'],
            'cycle_features_id': cycle_features_id.id,
        }
        _logger.debug(f"Novos valores: {novos_valores}")
        values.update(novos_valores)
       
        _logger.debug(f"valores atualizados: {values}")
        #ciclo não existe, cria novo ciclo
        _logger.debug(f"self.id: {self.id}")
        if not self.id:
            ciclo = self.create(values)
            _logger.debug(f"Ciclo não existe, criando novo ciclo. Ciclo criado: {ciclo.name}")
            return ciclo
        #ciclo existe, atualiza ciclo
        #verificando se ciclo finalizou
        
        
        values['state'] = 'em_andamento'
        if body['state'] == 'concluido':
            values['state'] = 'concluido'
        if body['state'] == 'abortado':
            values['state'] = 'abortado'
        
        if body['state'] == 'em_andamento':
            return self.write(values)
        
        try:
            _logger.debug(f"body: {body['fase']}")
            final_ciclo = list(filter(lambda x: x[1] == 'FINAL  DE CICLO', body['fase']))
            _logger.debug(f"final_ciclo: {final_ciclo}")
            if final_ciclo:
                values['end_date'] = final_ciclo[0][0] + timedelta(hours=3)
                return self.write(values)
            
        
            _logger.debug(f"ultima data_hora: {body['data'][-1][0]}")
            data_fim =body['data'][-1][0]
            data_fim_ajustada = data_fim + timedelta(hours=3)
            values['end_date'] = data_fim_ajustada     

        except Exception as e:
            _logger.error(f"Erro ao obter data de finalização do ciclo: {e}")
            values['end_date'] = self.start_date 
            values['state'] = 'erro'


        return self.write(values)
        
    def data_hora_to_datetime(self, data, hora):
        """
        Converte strings de data e hora em um objeto datetime.
        
        Args:
            data: Objeto de data
            hora: String no formato 'HH:MM:SS'
            
        Returns:
            datetime: Objeto datetime com a data e hora combinadas e ajustadas para o fuso horário
        """
        # Extraindo horas, minutos e segundos da string
        horas, minutos, segundos = map(int, hora.split(':'))
        
        # Combinando o objeto data com a hora extraída
        data_completa = datetime.combine(data, time(horas, minutos, segundos))
        
        
        # Convertendo para o formato compatível com fields.Datetime do Odoo
        
        
        # Adicionando 3 horas ao horário para compensar diferença de fuso
        _logger.debug(f"data_completa: {data_completa}")
        data_completa = data_completa + timedelta(hours=3)
        _logger.debug(f"data_completa + 3 horas: {data_completa}")
        return data_completa
    
 
class SupervisorioCiclosTermoDetalhes(models.Model):
    _name = 'afr.supervisorio.ciclos.termo.detalhes'
    _description = 'Detalhes do Ciclo de Termodesinfecção'

   
    termo_temperature = fields.Float('Temperatura de Esterilização (°C)', help='Temperatura alvo para esterilização')
   
    termo_phases = fields.Integer('Número de Fases de Vácuo', help='Número de fases de vácuo do ciclo')
    termo_drying_time = fields.Float('Tempo de Secagem (min)', help='Duração da fase de secagem') 
    