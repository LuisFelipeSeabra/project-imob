@echo off
REM Script de inicialização do sistema de fila de processamento

echo ========================================
echo Iniciando Sistema de Fila de Processamento
echo ========================================

REM Configurar variáveis de ambiente
set SUPABASE_URL=https://seu-projeto.supabase.co
set SUPABASE_KEY=sua-chave-secreta
set MESHROOM_PATH=C:\Program Files\Meshroom\Meshroom.exe
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado. Instale Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Instalar dependências se necessário
echo Verificando dependências...
pip install -r requirements.txt >nul 2>&1

REM Iniciar sistema de fila
echo Iniciando processador de fila...
python scripts\fila_processamento.py ^
    --supabase-url "%SUPABASE_URL%" ^
    --supabase-key "%SUPABASE_KEY%" ^
    --workers 3

pause
