# 🧪 Tutorial de Testes - Project Imob

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação](#instalação)
3. [Executando os Testes](#executando-os-testes)
4. [Tipos de Testes](#tipos-de-testes)
5. [Interpretando Resultados](#interpretando-resultados)
6. [Cobertura de Código](#cobertura-de-código)
7. [Troubleshooting](#troubleshooting)
8. [Boas Práticas](#boas-práticas)

---

## 📦 Pré-requisitos

### Software Necessário

| Software | Versão | Link |
|----------|--------|------|
| Python | 3.8+ | https://www.python.org |
| pip | 20.0+ | Incluído no Python |
| Git | 2.0+ | https://git-scm.com |

### Dependências Python

```bash
# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock

# Ou instalar todas as dependências
pip install -r requirements.txt
```

---

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/LuisFelipeSeabra/project-imob.git
cd project-imob
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar apenas dependências de teste
pip install pytest pytest-cov pytest-mock
```

---

## ▶️ Executando os Testes

### Comandos Básicos

```bash
# Executar todos os testes
pytest tests/ -v

# Executar testes específicos
pytest tests/test_processamento.py -v
pytest tests/test_fila.py -v

# Executar com cobertura
pytest tests/ -v --cov=scripts --cov-report=html

# Executar testes em paralelo (mais rápido)
pytest tests/ -v -n auto
```

### Comandos Avançados

```bash
# Executar apenas testes que falharam na última execução
pytest tests/ -v --lf

# Executar testes com mais detalhes
pytest tests/ -v -s

# Executar testes e parar no primeiro erro
pytest tests/ -v -x

# Executar testes com verbose aumentado
pytest tests/ -vv

# Executar testes com marcadores específicos
pytest tests/ -v -m "unit"
pytest tests/ -v -m "integration"
```

---

## 🧪 Tipos de Testes

### 1. **Testes de Processamento** (`test_processamento.py`)

Testa funcionalidades de processamento de fotos:

```python
# Testa validação de fotos
def test_validar_fotos_sucesso(self):
    fotos = validar_fotos(str(self.test_dir))
    self.assertEqual(len(fotos), 35)

# Testa validação com poucas fotos
def test_validar_fotos_insuficiente(self):
    fotos = validar_fotos(str(temp_dir))
    self.assertEqual(len(fotos), 0)

# Testa criação de diretórios
def test_criar_diretorios(self):
    criar_diretorios()
    self.assertTrue(Path("./output").exists())
```

### 2. **Testes de Fila** (`test_fila.py`)

Testa o sistema de fila de processamento:

```python
# Testa criação de job
def test_criar_job(self):
    job_id = self.processador.criar_job('imovel-123', 'fotos')
    self.assertEqual(job_id, 'test-job-id')

# Testa busca de próximo job
def test_buscar_proximo_job(self):
    job = self.processador._buscar_proximo_job()
    self.assertIsNotNone(job)

# Testa atualização de status
def test_atualizar_status(self):
    self.processador._atualizar_status('job-1', 'processando', 50)
```

---

## 📊 Interpretando Resultados

### Saída de Sucesso

```bash
tests/test_processamento.py::TestProcessamentoFotos::test_validar_fotos_sucesso PASSED [33%]
tests/test_processamento.py::TestProcessamentoFotos::test_validar_fotos_insuficiente PASSED [66%]
tests/test_processamento.py::TestProcessamentoFotos::test_criar_diretorios PASSED [100%]

============================== 3 passed in 0.15s ==============================
```

### Saída com Falhas

```bash
tests/test_processamento.py::TestProcessamentoFotos::test_validar_fotos_sucesso PASSED [33%]
tests/test_processamento.py::TestProcessamentoFotos::test_validar_fotos_insuficiente FAILED [66%]
tests/test_processamento.py::TestProcessamentoFotos::test_criar_diretorios PASSED [100%]

=================================== FAILURES ===================================
___________________ test_validar_fotos_insuficiente ___________________

    def test_validar_fotos_insuficiente(self):
        temp_dir = Path("./test_fotos_poucas")
        temp_dir.mkdir(exist_ok=True)
        
        for i in range(10):
            (temp_dir / f"foto_{i}.jpg").touch()
        
        fotos = validar_fotos(str(temp_dir))
>       self.assertEqual(len(fotos), 0)
E       AssertionError: 10 != 0

tests/test_processamento.py:45: AssertionError
```

### Interpretando Códigos

| Símbolo | Significado |
|---------|-------------|
| ✅ PASSED | Teste passou com sucesso |
| ❌ FAILED | Teste falhou |
| ⚠️ SKIPPED | Teste foi pulado |
| ⏱️ TIMEOUT | Teste excedeu tempo limite |

---

## 📈 Cobertura de Código

### Gerar Relatório de Cobertura

```bash
# Cobertura básica
pytest tests/ --cov=scripts

# Cobertura com relatório HTML
pytest tests/ --cov=scripts --cov-report=html

# Cobertura com relatório XML
pytest tests/ --cov=scripts --cov-report=xml

# Cobertura com relatório terminal
pytest tests/ --cov=scripts --cov-report=term-missing
```

### Interpretar Cobertura

```bash
Name                    Stmts   Miss  Cover
-------------------------------------------
scripts/processar_fotos.py    150     30    80%
scripts/fila_processamento.py 200     50    75%
-------------------------------------------
TOTAL                       350     80    77%
```

### Níveis de Cobertura

| Cobertura | Qualidade | Descrição |
|-----------|-----------|-----------|
| 90-100% | 🟢 Excelente | Código bem testado |
| 80-89% | 🟡 Bom | Código adequadamente testado |
| 70-79% | 🟠 Razoável | Código precisa de mais testes |
| <70% | 🔴 Insuficiente | Código precisa de mais testes |

---

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. **Erro: "No module named 'pytest'"**
```bash
# Solução: Instalar pytest
pip install pytest
```

#### 2. **Erro: "No module named 'processar_fotos'"**
```bash
# Solução: Verificar se está no diretório correto
cd project-imob
pytest tests/ -v
```

#### 3. **Erro: "Permission denied"**
```bash
# Solução: Executar como administrador (Windows)
# Ou verificar permissões de arquivo
chmod +x scripts/*.py
```

#### 4. **Erro: "Supabase connection failed"**
```bash
# Solução: Verificar variáveis de ambiente
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

#### 5. **Erro: "Meshroom not found"**
```bash
# Solução: Verificar caminho no .env
echo $MESHROOM_PATH
# Ou definir manualmente
set MESHROOM_PATH=C:\Program Files\Meshroom\Meshroom.exe
```

### Logs de Debug

```bash
# Executar com debug detalhado
pytest tests/ -v -s --log-cli-level=DEBUG

# Executar com mais informações
pytest tests/ -vv --tb=long

# Executar e capturar saída
pytest tests/ -v > test_results.txt
```

---

## 📝 Boas Práticas

### 1. **Estrutura de Testes**

```python
# Organizar testes por funcionalidade
class TestProcessamentoFotos(unittest.TestCase):
    def setUp(self):
        """Configuração inicial"""
        pass
    
    def tearDown(self):
        """Limpeza após teste"""
        pass
    
    def test_funcionalidade_especifica(self):
        """Testa funcionalidade específica"""
        pass
```

### 2. **Nomenclatura**

```python
# Nomes descritivos
def test_validar_fotos_sucesso(self):
    """Testa validação com número suficiente de fotos"""
    pass

def test_validar_fotos_insuficiente(self):
    """Testa validação com número insuficiente de fotos"""
    pass
```

### 3. **Asserções**

```python
# Usar asserções específicas
self.assertEqual(resultado, esperado)
self.assertTrue(condicao)
self.assertFalse(condicao)
self.assertIn(item, lista)
self.assertRaises(Exception, funcao)
```

### 4. **Fixtures**

```python
import pytest

@pytest.fixture
def imovel_mock():
    """Fixture para dados de teste"""
    return {
        'id': 'test-imovel',
        'titulo': 'Imóvel Teste',
        'area_m2': 100
    }

def test_com_fixture(imovel_mock):
    """Testa usando fixture"""
    assert imovel_mock['id'] == 'test-imovel'
```

### 5. **Parametrização**

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (10, 0),      # Poucas fotos
    (30, 30),     # Mínimo
    (50, 50),     # Ideal
    (100, 100),   # Máximo
])
def test_validar_fotos_parametrizado(input, expected):
    """Testa validação com diferentes quantidades"""
    resultado = validar_fotos(input)
    assert resultado == expected
```

---

## 🎯 Comandos Rápidos

```bash
# Teste rápido
pytest tests/ -v

# Teste com cobertura
pytest tests/ -v --cov=scripts

# Teste e relatório HTML
pytest tests/ -v --cov=scripts --cov-report=html

# Abrir relatório HTML
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

---

## 📚 Recursos Adicionais

- [Documentação do pytest](https://docs.pytest.org/)
- [Guia de Testes Python](https://realpython.com/python-testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 📞 Suporte

Para dúvidas sobre testes:

1. **Verifique os logs** em `fila_processamento.log`
2. **Execute com debug** `pytest tests/ -v -s --log-cli-level=DEBUG`
3. **Consulte a documentação** em `docs/`
4. **Abra uma issue** no GitHub

---

**Status:** ✅ Documentação completa de testes implementada.