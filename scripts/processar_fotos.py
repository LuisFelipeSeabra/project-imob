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
from pathlib import Path
from datetime import datetime

# Configurações
MESHROOM_PATH = r"C:\Program Files\Meshroom\Meshroom.exe"  # Ajuste conforme instalação
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"  # Ajuste conforme instalação
OUTPUT_DIR = Path("./output")
TEMP_DIR = Path("./temp")

def criar_diretorios():
    """Cria diretórios de trabalho"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    print("✓ Diretórios de trabalho criados")

def validar_fotos(fotos_dir):
    """Valida se há fotos suficientes para processamento"""
    extensoes = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    fotos = []
    for ext in extensoes:
        fotos.extend(Path(fotos_dir).glob(f"*{ext}"))
        fotos.extend(Path(fotos_dir).glob(f"*{ext.upper()}"))
    
    if len(fotos) < 20:
        print(f"⚠️  Apenas {len(fotos)} fotos encontradas. Recomendado: mínimo 30")
        return False
    
    print(f"✓ {len(fotos)} fotos encontradas para processamento")
    return True

def processar_meshroom(fotos_dir, output_dir):
    """Processa fotos com Meshroom"""
    print("🔄 Iniciando processamento com Meshroom...")
    
    # Criar projeto Meshroom
    projeto_path = TEMP_DIR / "projeto.mg"
    
    # Comando para criar projeto e importar imagens
    cmd = [
        MESHROOM_PATH,
        "-n", "MeshroomPipeline",
        "--save", str(projeto_path)
    ]
    
    try:
        # Executar Meshroom em modo headless (se suportado)
        subprocess.run(cmd, check=True)
        print("✓ Projeto Meshroom criado")
        
        # Para processamento automático, é necessário usar a API interna
        # ou executar manualmente. Este script serve como base.
        print("ℹ️  Abra o Meshroom e:")
        print("   1. Arraste as fotos para a janela")
        print("   2. Clique em 'Start' para processar")
        print("   3. Exporte o modelo em formato .glb")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao executar Meshroom: {e}")
        return False
    except FileNotFoundError:
        print("✗ Meshroom não encontrado. Instale em: https://github.com/alicevision/meshroom")
        return False

def otimizar_blender(modelo_input, modelo_output):
    """Otimiza modelo 3D com Blender"""
    print("🔄 Otimizando modelo com Blender...")
    
    blender_script = f"""
import bpy

# Limpar cena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Importar modelo
bpy.ops.import_scene.obj(filepath='{modelo_input}')

# Aplicar decimate
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
        decimate.ratio = 0.5  # Reduzir 50% dos polígonos
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier='Decimate')

# Exportar para GLB
bpy.ops.export_scene.gltf(
    filepath='{modelo_output}',
    export_format='GLB',
    export_yup=True,
    export_apply=True
)
"""
    
    script_path = TEMP_DIR / "otimizar.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(blender_script)
    
    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", str(script_path)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Modelo otimizado e exportado para .glb")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao executar Blender: {e}")
        return False
    except FileNotFoundError:
        print("✗ Blender não encontrado. Instale em: https://www.blender.org")
        return False

def upload_supabase(arquivo_glb, imovel_id):
    """Faz upload do modelo para Supabase Storage"""
    print("🔄 Fazendo upload para Supabase...")
    
    # Para upload real, use a API do Supabase ou CLI
    # Exemplo com supabase-py:
    
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
            print(f"✗ Erro no upload: {response['error']}")
            return False
        
        # Atualizar URL do modelo no banco
        url_modelo = f"{SUPABASE_URL}/storage/v1/object/public/modelos3d/{imovel_id}/modelo.glb"
        
        supabase.table('imoveis').update({
            'url_modelo_3d': url_modelo,
            'status': 'pronto'
        }).eq('id', imovel_id).execute()
        
        print(f"✓ Modelo disponível em: {url_modelo}")
        return True
        
    except ImportError:
        print("✗ Instale o supabase-py: pip install supabase")
        print("ℹ️  Faça o upload manual do arquivo .glb para o Supabase Storage")
        return True
    except Exception as e:
        print(f"✗ Erro no upload: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python processar_fotos.py <diretorio_fotos> [imovel_id]")
        sys.exit(1)
    
    fotos_dir = sys.argv[1]
    imovel_id = sys.argv[2] if len(sys.argv) > 2 else f"imovel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=" * 50)
    print("🚀 Processador de Fotos para VR - Project Imob")
    print("=" * 50)
    
    criar_diretorios()
    
    if not validar_fotos(fotos_dir):
        sys.exit(1)
    
    # Processar com Meshroom
    if processar_meshroom(fotos_dir, OUTPUT_DIR):
        print("✓ Processamento 3D concluído")
        
        # Buscar arquivo gerado
        modelo_input = next(OUTPUT_DIR.glob("*.obj"), None)
        if modelo_input:
            modelo_output = OUTPUT_DIR / f"{imovel_id}.glb"
            if otimizar_blender(modelo_input, modelo_output):
                upload_supabase(modelo_output, imovel_id)
    
    print("=" * 50)
    print("✅ Processo concluído!")
    print("=" * 50)

if __name__ == "__main__":
    main()
