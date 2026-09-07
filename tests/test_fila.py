import unittest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar diretório scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from fila_processamento import ProcessadorFila

class TestFilaProcessamento(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.supabase_url = "https://test.supabase.co"
        self.supabase_key = "test-key"
        
        # Mock do Supabase
        self.supabase_patcher = patch('fila_processamento.create_client')
        self.mock_supabase = self.supabase_patcher.start()
        self.mock_client = MagicMock()
        self.mock_supabase.return_value = self.mock_client
        
        self.processador = ProcessadorFila(self.supabase_url, self.supabase_key)
    
    def tearDown(self):
        """Limpeza após os testes"""
        self.supabase_patcher.stop()
        self.processador.parar()
    
    def test_inicializacao(self):
        """Testa inicialização do processador"""
        self.assertIsNotNone(self.processador)
        self.assertEqual(self.processador.max_workers, 3)
        self.assertFalse(self.processador.running)
    
    def test_criar_job(self):
        """Testa criação de job"""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.data = [{'id': 'test-job-id'}]
        self.mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        job_id = self.processador.criar_job('imovel-123', 'fotos', {'test': 'data'})
        
        self.assertEqual(job_id, 'test-job-id')
        self.mock_client.table.assert_called_with('processamento')
    
    def test_buscar_proximo_job(self):
        """Testa busca de próximo job"""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.data = [{'id': 'job-1', 'status': 'pendente'}]
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        job = self.processador._buscar_proximo_job()
        
        self.assertIsNotNone(job)
        self.assertEqual(job['id'], 'job-1')
    
    def test_buscar_proximo_job_vazio(self):
        """Testa busca quando não há jobs"""
        # Mock da resposta vazia
        mock_response = MagicMock()
        mock_response.data = []
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        job = self.processador._buscar_proximo_job()
        
        self.assertIsNone(job)
    
    def test_atualizar_status(self):
        """Testa atualização de status"""
        self.processador._atualizar_status('job-1', 'processando', 50)
        
        self.mock_client.table.assert_called_with('processamento')
        self.mock_client.table.return_value.update.assert_called()
    
    def test_atualizar_progresso(self):
        """Testa atualização de progresso"""
        self.processador._atualizar_progresso('job-1', 75)
        
        self.mock_client.table.assert_called_with('processamento')
        self.mock_client.table.return_value.update.assert_called()
    
    def test_registrar_inicio(self):
        """Testa registro de início"""
        self.processador._registrar_inicio('job-1')
        
        self.mock_client.table.assert_called_with('processamento')
        self.mock_client.table.return_value.update.assert_called()
    
    def test_registrar_fim_sucesso(self):
        """Testa registro de fim com sucesso"""
        self.processador._registrar_fim('job-1', True)
        
        self.mock_client.table.assert_called_with('processamento')
        self.mock_client.table.return_value.update.assert_called()
    
    def test_registrar_fim_erro(self):
        """Testa registro de fim com erro"""
        self.processador._registrar_fim('job-1', False, 'Erro de teste')
        
        self.mock_client.table.assert_called_with('processamento')
        self.mock_client.table.return_value.update.assert_called()
    
    def test_verificar_jobs_travados(self):
        """Testa verificação de jobs travados"""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.data = [{'id': 'job-1'}]
        self.mock_client.table.return_value.update.return_value.eq.return_value.lt.return_value.execute.return_value = mock_response
        
        self.processador._verificar_jobs_travados()
        
        self.mock_client.table.assert_called_with('processamento')
    
    def test_verificar_jobs_retry(self):
        """Testa verificação de jobs para retry"""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.data = [{'id': 'job-1', 'tentativas': 1, 'max_tentativas': 3}]
        self.mock_client.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value = mock_response
        
        self.processador._verificar_jobs_retry()
        
        self.mock_client.table.assert_called_with('processamento')
    
    def test_limpar_logs_antigos(self):
        """Testa limpeza de logs antigos"""
        self.processador._limpar_logs_antigos()
        
        self.mock_client.table.assert_called_with('logs')
        self.mock_client.table.return_value.delete.assert_called()

if __name__ == '__main__':
    unittest.main()
