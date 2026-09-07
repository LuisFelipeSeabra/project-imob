#!/usr/bin/env python3
"""
Sistema de Fila de Processamento
Processa jobs de processamento 3D de forma assíncrona
"""

import os
import sys
import time
import logging
import json
import signal
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('fila_processamento.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessadorFila:
    """
    Processador de fila de trabalhos de processamento 3D
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Inicializa o processador de fila
        
        Args:
            supabase_url: URL do Supabase
            supabase_key: Chave de serviço do Supabase
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.running = False
        self.thread = None
        self.max_workers = 3
        self.workers = []
        
        # Importar Supabase
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("Conectado ao Supabase")
        except ImportError:
            logger.error("Supabase não instalado. Execute: pip install supabase")
            raise
        
        # Registrar handlers de sinal
        signal.signal(signal.SIGINT, self.parar)
        signal.signal(signal.SIGTERM, self.parar)
    
    def iniciar(self):
        """Inicia o processador de fila"""
        logger.info("Iniciando processador de fila...")
        self.running = True
        
        # Iniciar workers
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            logger.info(f"Worker {i} iniciado")
        
        # Thread principal
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Processador de fila iniciado")
    
    def parar(self, signum=None, frame=None):
        """Para o processador de fila"""
        logger.info("Parando processador de fila...")
        self.running = False
        
        # Aguardar workers terminarem
        for worker in self.workers:
            worker.join(timeout=5)
        
        logger.info("Processador de fila parado")
        sys.exit(0)
    
    def _worker_loop(self, worker_id: int):
        """
        Loop principal do worker
        
        Args:
            worker_id: ID do worker
        """
        logger.info(f"Worker {worker_id} aguardando jobs...")
        
        while self.running:
            try:
                # Buscar próximo job
                job = self._buscar_proximo_job()
                
                if job:
                    logger.info(f"Worker {worker_id} processando job {job['id']}")
                    self._processar_job(job)
                else:
                    # Sem jobs, aguardar
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"Erro no worker {worker_id}: {e}")
                time.sleep(10)
    
    def _monitor_loop(self):
        """Loop de monitoramento do sistema"""
        while self.running:
            try:
                # Verificar jobs travados
                self._verificar_jobs_travados()
                
                # Verificar jobs com erro para retry
                self._verificar_jobs_retry()
                
                # Limpar logs antigos
                self._limpar_logs_antigos()
                
                # Aguardar antes de verificar novamente
                time.sleep(300)  # 5 minutos
                
            except Exception as e:
                logger.error(f"Erro no monitor: {e}")
                time.sleep(60)
    
    def _buscar_proximo_job(self) -> Optional[Dict]:
        """
        Busca o próximo job pendente na fila
        
        Returns:
            Job pendente ou None se não houver
        """
        try:
            # Buscar job com menor prioridade e mais antigo
            response = self.supabase.table('processamento')\
                .select('*')\
                .eq('status', 'pendente')\
                .order('created_at', ascending=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar job: {e}")
            return None
    
    def _processar_job(self, job: Dict):
        """
        Processa um job da fila
        
        Args:
            job: Job a ser processado
        """
        job_id = job['id']
        imovel_id = job['imovel_id']
        tipo = job['tipo']
        
        try:
            # Marcar como processando
            self._atualizar_status(job_id, 'processando', progresso=0)
            
            # Registrar início
            self._registrar_inicio(job_id)
            
            # Processar conforme tipo
            if tipo == 'fotos':
                self._processar_fotos(job)
            elif tipo == 'modelo_3d':
                self._processar_modelo_3d(job)
            elif tipo == 'tour_360':
                self._processar_tour_360(job)
            else:
                raise ValueError(f"Tipo de job desconhecido: {tipo}")
            
            # Marcar como concluído
            self._atualizar_status(job_id, 'concluido', progresso=100)
            self._registrar_fim(job_id, sucesso=True)
            
            logger.info(f"Job {job_id} concluído com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao processar job {job_id}: {e}")
            
            # Verificar se deve tentar novamente
            tentativas = job.get('tentativas', 0)
            max_tentativas = job.get('max_tentativas', 3)
            
            if tentativas < max_tentativas:
                # Incrementar tentativas e voltar para pendente
                self.supabase.table('processamento')\
                    .update({
                        'tentativas': tentativas + 1,
                        'status': 'pendente',
                        'erro_mensagem': str(e),
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', job_id)\
                    .execute()
                
                logger.info(f"Job {job_id} reagendado (tentativa {tentativas + 1}/{max_tentativas})")
            else:
                # Marcar como erro
                self._atualizar_status(job_id, 'erro', erro_mensagem=str(e))
                self._registrar_fim(job_id, sucesso=False, erro=str(e))
    
    def _processar_fotos(self, job: Dict):
        """
        Processa fotos de um imóvel
        
        Args:
            job: Job de processamento
        """
        imovel_id = job['imovel_id']
        input_data = job.get('input_data', {})
        
        logger.info(f"Processando fotos do imóvel {imovel_id}")
        
        # Buscar fotos do imóvel
        fotos = self.supabase.table('fotos_captura')\
            .select('*')\
            .eq('imovel_id', imovel_id)\
            .eq('processada', False)\
            .execute()
        
        if not fotos.data:
            raise Exception("Nenhuma foto encontrada para processamento")
        
        # Atualizar progresso
        self._atualizar_progresso(job['id'], 10)
        
        # Baixar fotos
        fotos_dir = TEMP_DIR / f"fotos_{imovel_id}"
        fotos_dir.mkdir(exist_ok=True)
        
        for i, foto in enumerate(fotos.data):
            self._baixar_foto(foto['url_foto'], fotos_dir / f"foto_{i:03d}.jpg")
            self._atualizar_progresso(job['id'], 10 + (i / len(fotos.data)) * 20)
        
        self._atualizar_progresso(job['id'], 30)
        
        # Processar com Meshroom
        modelo_path = self._processar_meshroom(fotos_dir, imovel_id)
        
        self._atualizar_progresso(job['id'], 70)
        
        # Otimizar com Blender
        if modelo_path:
            modelo_otimizado = self._otimizar_blender(modelo_path, imovel_id)
            self._atualizar_progresso(job['id'], 90)
            
            # Upload para Supabase
            if modelo_otimizado:
                self._upload_modelo(modelo_otimizado, imovel_id)
                self._atualizar_progresso(job['id'], 100)
        
        # Marcar fotos como processadas
        self.supabase.table('fotos_captura')\
            .update({'processada': True})\
            .eq('imovel_id', imovel_id)\
            .execute()
    
    def _processar_modelo_3d(self, job: Dict):
        """
        Processa modelo 3D de um imóvel
        
        Args:
            job: Job de processamento
        """
        imovel_id = job['imovel_id']
        input_data = job.get('input_data', {})
        
        logger.info(f"Processando modelo 3D do imóvel {imovel_id}")
        
        # Buscar modelo existente
        modelo_path = input_data.get('modelo_path')
        
        if not modelo_path or not Path(modelo_path).exists():
            raise Exception("Modelo 3D não encontrado")
        
        self._atualizar_progresso(job['id'], 30)
        
        # Otimizar modelo
        modelo_otimizado = self._otimizar_blender(Path(modelo_path), imovel_id)
        
        self._atualizar_progresso(job['id'], 70)
        
        # Upload para Supabase
        if modelo_otimizado:
            self._upload_modelo(modelo_otimizado, imovel_id)
            self._atualizar_progresso(job['id'], 100)
    
    def _processar_tour_360(self, job: Dict):
        """
        Processa tour 360 de um imóvel
        
        Args:
            job: Job de processamento
        """
        imovel_id = job['imovel_id']
        input_data = job.get('input_data', {})
        
        logger.info(f"Processando tour 360 do imóvel {imovel_id}")
        
        # Implementar processamento de tour 360
        # Por enquanto, apenas marcar como concluído
        self._atualizar_progresso(job['id'], 100)
    
    def _baixar_foto(self, url: str, destino: Path):
        """
        Baixa uma foto do Supabase Storage
        
        Args:
            url: URL da foto
            destino: Caminho de destino
        """
        try:
            import requests
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(destino, 'wb') as f:
                f.write(response.content)
                
        except Exception as e:
            logger.error(f"Erro ao baixar foto {url}: {e}")
            raise
    
    def _processar_meshroom(self, fotos_dir: Path, imovel_id: str) -> Optional[Path]:
        """
        Processa fotos com Meshroom
        
        Args:
            fotos_dir: Diretório com as fotos
            imovel_id: ID do imóvel
            
        Returns:
            Caminho do modelo gerado ou None
        """
        try:
            from processar_fotos import processar_meshroom_automatico
            return processar_meshroom_automatico(str(fotos_dir), TEMP_DIR)
        except Exception as e:
            logger.error(f"Erro no processamento Meshroom: {e}")
            return None
    
    def _otimizar_blender(self, modelo_path: Path, imovel_id: str) -> Optional[Path]:
        """
        Otimiza modelo com Blender
        
        Args:
            modelo_path: Caminho do modelo
            imovel_id: ID do imóvel
            
        Returns:
            Caminho do modelo otimizado ou None
        """
        try:
            from processar_fotos import otimizar_blender
            modelo_output = TEMP_DIR / f"{imovel_id}_otimizado.glb"
            
            if otimizar_blender(modelo_path, modelo_output):
                return modelo_output
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na otimização Blender: {e}")
            return None
    
    def _upload_modelo(self, modelo_path: Path, imovel_id: str):
        """
        Faz upload do modelo para Supabase
        
        Args:
            modelo_path: Caminho do modelo
            imovel_id: ID do imóvel
        """
        try:
            with open(modelo_path, 'rb') as f:
                self.supabase.storage.from_('modelos3d').upload(
                    f"{imovel_id}/modelo.glb",
                    f,
                    {"content-type": "model/gltf-binary"}
                )
            
            # Atualizar registro
            url_modelo = f"{self.supabase_url}/storage/v1/object/public/modelos3d/{imovel_id}/modelo.glb"
            
            self.supabase.table('imoveis').update({
                'url_modelo_3d': url_modelo,
                'status': 'pronto',
                'tamanho_modelo': modelo_path.stat().st_size,
                'formato_modelo': 'glb',
                'updated_at': datetime.now().isoformat()
            }).eq('id', imovel_id).execute()
            
            logger.info(f"Modelo {imovel_id} enviado para Supabase")
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            raise
    
    def _atualizar_status(self, job_id: str, status: str, progresso: int = 0, erro_mensagem: str = None):
        """
        Atualiza status do job
        
        Args:
            job_id: ID do job
            status: Novo status
            progresso: Progresso (0-100)
            erro_mensagem: Mensagem de erro (se houver)
        """
        try:
            dados = {
                'status': status,
                'progresso': progresso,
                'updated_at': datetime.now().isoformat()
            }
            
            if erro_mensagem:
                dados['erro_mensagem'] = erro_mensagem
            
            self.supabase.table('processamento')\
                .update(dados)\
                .eq('id', job_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
    
    def _atualizar_progresso(self, job_id: str, progresso: int):
        """
        Atualiza apenas o progresso do job
        
        Args:
            job_id: ID do job
            progresso: Progresso (0-100)
        """
        self._atualizar_status(job_id, 'processando', progresso)
    
    def _registrar_inicio(self, job_id: str):
        """
        Registra início do processamento
        
        Args:
            job_id: ID do job
        """
        try:
            self.supabase.table('processamento')\
                .update({'started_at': datetime.now().isoformat()})\
                .eq('id', job_id)\
                .execute()
        except Exception as e:
            logger.error(f"Erro ao registrar início: {e}")
    
    def _registrar_fim(self, job_id: str, sucesso: bool, erro: str = None):
        """
        Registra fim do processamento
        
        Args:
            job_id: ID do job
            sucesso: Se processamento foi bem-sucedido
            erro: Mensagem de erro (se houver)
        """
        try:
            dados = {
                'finished_at': datetime.now().isoformat()
            }
            
            if erro:
                dados['erro_mensagem'] = erro
            
            self.supabase.table('processamento')\
                .update(dados)\
                .eq('id', job_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao registrar fim: {e}")
    
    def _verificar_jobs_travados(self):
        """Verifica e reseta jobs travados"""
        try:
            # Jobs travados há mais de 1 hora
            limite = datetime.now() - timedelta(hours=1)
            
            response = self.supabase.table('processamento')\
                .update({'status': 'pendente'})\
                .eq('status', 'processando')\
                .lt('started_at', limite.isoformat())\
                .execute()
            
            if response.data:
                logger.warning(f"{len(response.data)} jobs travados resetados")
                
        except Exception as e:
            logger.error(f"Erro ao verificar jobs travados: {e}")
    
    def _verificar_jobs_retry(self):
        """Verifica jobs com erro para retry"""
        try:
            # Jobs com erro que podem ser retentados
            response = self.supabase.table('processamento')\
                .select('*')\
                .eq('status', 'erro')\
                .lt('tentativas', 'max_tentativas')\
                .execute()
            
            for job in response.data:
                # Reagendar job
                self.supabase.table('processamento')\
                    .update({
                        'status': 'pendente',
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', job['id'])\
                    .execute()
                
                logger.info(f"Job {job['id']} reagendado para retry")
                
        except Exception as e:
            logger.error(f"Erro ao verificar jobs retry: {e}")
    
    def _limpar_logs_antigos(self):
        """Limpa logs antigos"""
        try:
            # Logs mais antigos que 30 dias
            limite = datetime.now() - timedelta(days=30)
            
            self.supabase.table('logs')\
                .delete()\
                .lt('created_at', limite.isoformat())\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao limpar logs: {e}")
    
    def criar_job(self, imovel_id: str, tipo: str, input_data: Dict = None) -> str:
        """
        Cria um novo job na fila
        
        Args:
            imovel_id: ID do imóvel
            tipo: Tipo de processamento
            input_data: Dados de entrada
            
        Returns:
            ID do job criado
        """
        try:
            response = self.supabase.table('processamento')\
                .insert({
                    'imovel_id': imovel_id,
                    'tipo': tipo,
                    'status': 'pendente',
                    'input_data': input_data or {},
                    'created_at': datetime.now().isoformat()
                })\
                .execute()
            
            job_id = response.data[0]['id']
            logger.info(f"Job {job_id} criado para imóvel {imovel_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Erro ao criar job: {e}")
            raise

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Processador de Fila')
    parser.add_argument('--supabase-url', required=True, help='URL do Supabase')
    parser.add_argument('--supabase-key', required=True, help='Chave do Supabase')
    parser.add_argument('--workers', type=int, default=3, help='Número de workers')
    parser.add_argument('--daemon', action='store_true', help='Executar como daemon')
    
    args = parser.parse_args()
    
    # Criar processador
    processador = ProcessadorFila(args.supabase_url, args.supabase_key)
    processador.max_workers = args.workers
    
    # Iniciar
    processador.iniciar()
    
    if args.daemon:
        # Executar como daemon
        logger.info("Executando como daemon...")
        while True:
            time.sleep(60)
    else:
        # Executar interativo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            processador.parar()

if __name__ == "__main__":
    main()
