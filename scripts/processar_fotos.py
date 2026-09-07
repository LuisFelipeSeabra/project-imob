#!/usr/bin/env python3
"""
Script para processar fotos de imóveis com Meshroom
e gerar modelo 3D para visualização VR
"""

import os
import sys
import subprocess
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processamento.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações
MESHROOM_PATH = os.getenv("MESHROOM_PATH", r"C:\Program Files\Meshroom\Meshroom.exe")
BLENDER_PATH = os.getenv("BLENDER_PATH", r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe")
OUTPUT_DIR = Path("./output")
TEMP_DIR = Path("./temp")

def criar_diretorios() -> None:
    """Cria diretórios de trabalho"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    logger.info("Diretórios de trabalho criados")

def validar_fotos(fotos_dir: str) -> List[Path]:
    """
    Valida se há fotos suficientes para processamento
    
    Args:
        fotos_dir: Diretório contendo as fotos
        
    Returns:
        Lista de arquivos de foto válidos
    """
    extensoes = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    fotos = []
    
    for ext in extensoes:
        fotos.extend(Path(fotos_dir).glob(f"*{ext}"))
        fotos.extend(Path(fotos_dir).glob(f"*{ext.upper()}"))
    
    if len(fotos) < 20:
        logger.warning(f"Apenas {len(fotos)} fotos encontradas. Recomendado: mínimo 30")
        return []
    
    logger.info(f"{len(fotos)} fotos encontradas para processamento")
    return sorted(fotos)

def processar_meshroom_automatico(fotos_dir: str, output_dir: Path) -> Optional[Path]:
    """
    Processa fotos com Meshroom usando CLI
    
    Args:
        fotos_dir: Diretório com as fotos
        output_dir: Diretório de saída
        
    Returns:
        Caminho do arquivo OBJ gerado ou None se falhar
    """
    logger.info("Iniciando processamento automático com Meshroom...")
    
    # Criar projeto Meshroom
    projeto_path = TEMP_DIR / "projeto.mg"
    
    try:
        # Comando para processar automaticamente
        # Nota: Meshroom CLI tem limitações, pode ser necessário usar API interna
        cmd = [
            MESHROOM_PATH,
            "--input", fotos_dir,
            "--output", str(output_dir),
            "--save", str(projeto_path),
            "--forceCompute",
            "--pipeline", "MeshroomPipeline"
        ]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        
        # Executar com timeout de 30 minutos
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutos
        )
        
        logger.info("Processamento Meshroom concluído")
        
        # Buscar arquivo OBJ gerado
        obj_files = list(output_dir.glob("*.obj"))
        if obj_files:
            return obj_files[0]
        else:
            logger.error("Nenhum arquivo OBJ encontrado após processamento")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Processamento excedeu o tempo limite de 30 minutos")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar Meshroom: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logger.error("Meshroom não encontrado. Instale em: https://github.com/alicevision/meshroom")
        return None

def processar_meshroom_manual(fotos_dir: str, output_dir: Path) -> Optional[Path]:
    """
    Processa fotos com Meshroom manualmente (fallback)
    
    Args:
        fotos_dir: Diretório com as fotos
        output_dir: Diretório de saída
        
    Returns:
        Caminho do arquivo OBJ gerado ou None se falhar
    """
    logger.info("Iniciando processamento manual com Meshroom...")
    
    try:
        # Criar projeto Meshroom
        projeto_path = TEMP_DIR / "projeto.mg"
        
        # Comando para abrir Meshroom
        cmd = [MESHROOM_PATH]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        
        logger.info("Meshroom aberto. Por favor:")
        logger.info("1. Arraste as fotos para a janela")
        logger.info("2. Clique em 'Start' para processar")
        logger.info("3. Aguarde o processamento")
        logger.info("4. Exporte o modelo em formato .glb")
        logger.info(f"5. Salve em: {output_dir}")
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao abrir Meshroom: {e}")
        return None

def otimizar_blender(modelo_input: Path, modelo_output: Path) -> bool:
    """
    Otimiza modelo 3D com Blender
    
    Args:
        modelo_input: Caminho do arquivo de entrada
        modelo_output: Caminho do arquivo de saída
        
    Returns:
        True se sucesso, False caso contrário
    """
    logger.info("Otimizando modelo com Blender...")
    
    blender_script = f'''
import bpy
import sys

# Limpar cena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Importar modelo
try:
    bpy.ops.import_scene.obj(filepath='{modelo_input}')
    print("Modelo importado com sucesso")
except Exception as e:
    print(f"Erro ao importar modelo: {{e}}")
    sys.exit(1)

# Aplicar decimate
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        print(f"Processando objeto: {{obj.name}}")
        
        # Aplicar decimate
        decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
        decimate.ratio = 0.5  # Reduzir 50% dos polígonos
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier='Decimate')
        
        print(f"Polígonos reduzidos em {{obj.name}}")

# Exportar para GLB
try:
    bpy.ops.export_scene.gltf(
        filepath='{modelo_output}',
        export_format='GLB',
        export_yup=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False
    )
    print("Modelo exportado para GLB com sucesso")
except Exception as e:
    print(f"Erro ao exportar modelo: {{e}}")
    sys.exit(1)
'''
    
    script_path = TEMP_DIR / "otimizar.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(blender_script)
    
    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", str(script_path)
    ]
    
    try:
        logger.info(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos
        )
        
        logger.info("Modelo otimizado e exportado para .glb")
        logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Otimização excedeu o tempo limite de 10 minutos")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar Blender: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("Blender não encontrado. Instale em: https://www.blender.org")
        return False

def upload_supabase(arquivo_glb: Path, imovel_id: str) -> bool:
    """
    Faz upload do modelo para Supabase Storage
    
    Args:
        arquivo_glb: Caminho do arquivo GLB
        imovel_id: ID do imóvel
        
    Returns:
        True se sucesso, False caso contrário
    """
    logger.info("Fazendo upload para Supabase...")
    
    try:
        from supabase import create_client, Client
        
        # Configure suas credenciais do Supabase
        SUPABASE_URL = os.getenv("SUPABASE_URL", "https://seu-projeto.supabase.co")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sua-chave-secreta")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Upload para bucket 'modelos3d'
        with open(arquivo_glb, 'rb') as f:
            response = supabase.storage.from_('modelos3d').upload(
                f"{imovel_id}/modelo.glb",
                f,
                {"content-type": "model/gltf-binary"}
            )
        
        if response.get('error'):
            logger.error(f"Erro no upload: {response['error']}")
            return False
        
        # Atualizar URL do modelo no banco
        url_modelo = f"{SUPABASE_URL}/storage/v1/object/public/modelos3d/{imovel_id}/modelo.glb"
        
        supabase.table('imoveis').update({
            'url_modelo_3d': url_modelo,
            'status': 'pronto',
            'tamanho_modelo': arquivo_glb.stat().st_size,
            'formato_modelo': 'glb'
        }).eq('id', imovel_id).execute()
        
        logger.info(f"Modelo disponível em: {url_modelo}")
        return True
        
    except ImportError:
        logger.error("Instale o supabase-py: pip install supabase")
        logger.info("Faça o upload manual do arquivo .glb para o Supabase Storage")
        return True
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python processar_fotos.py <diretorio_fotos> [imovel_id] [--auto]")
        print("  --auto: processamento automático (experimental)")
        sys.exit(1)
    
    fotos_dir = sys.argv[1]
    imovel_id = sys.argv[2] if len(sys.argv) > 2 else f"imovel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    modo_auto = '--auto' in sys.argv
    
    logger.info("=" * 50)
    logger.info("Processador de Fotos para VR - Project Imob")
    logger.info("=" * 50)
    
    criar_diretorios()
    
    fotos = validar_fotos(fotos_dir)
    if not fotos:
        sys.exit(1)
    
    # Processar com Meshroom
    modelo_input = None
    
    if modo_auto:
        modelo_input = processar_meshroom_automatico(fotos_dir, OUTPUT_DIR)
    else:
        modelo_input = processar_meshroom_manual(fotos_dir, OUTPUT_DIR)
    
    if modelo_input:
        logger.info("Processamento 3D concluído")
        
        # Buscar arquivo gerado
        modelo_output = OUTPUT_DIR / f"{imovel_id}.glb"
        if otimizar_blender(modelo_input, modelo_output):
            upload_supabase(modelo_output, imovel_id)
    else:
        logger.warning("Processamento manual iniciado. Complete no Meshroom e execute novamente.")
    
    logger.info("=" * 50)
    logger.info("Processo concluído!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
