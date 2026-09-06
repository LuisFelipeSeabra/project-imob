# Guia de Instalação - Project Imob

## Pré-requisitos

### Para Visualização (Frontend)
- Navegador moderno (Chrome, Firefox, Edge, Safari)
- Conexão com internet
- Dispositivo compatível:
  - Desktop: mouse e teclado
  - Mobile: tela touch e giroscópio
  - VR: Meta Quest, Oculus, ou Google Cardboard

### Para Processamento 3D (Backend)
- Windows 10/11 (64-bit)
- Python 3.8 ou superior
- GPU NVIDIA com pelo menos 4GB VRAM (recomendado)
- 16GB RAM ou superior
- 50GB de espaço em disco

### Software Necessário

| Software | Versão | Link |
|----------|--------|------|
| Meshroom | 2023.3.0+ | https://github.com/alicevision/meshroom |
| Blender | 4.0+ | https://www.blender.org |
| Python | 3.8+ | https://www.python.org |
| Git | 2.0+ | https://git-scm.com |

## Instalação Passo a Passo

### 1. Clonar o Repositório

```bash
git clone https://github.com/LuisFelipeSeabra/project-imob.git
cd project-imob
```

### 2. Configurar o Frontend

```bash
cd frontend
npx serve .
```

Acesse: http://localhost:3000

### 3. Configurar o Backend (Supabase)

#### 3.1 Criar Projeto no Supabase

1. Acesse https://supabase.com
2. Crie uma conta gratuita
3. Clique em "New Project"
4. Preencha:
   - Nome: `project-imob`
   - Database Password: (gere uma senha forte)
   - Região: `South America (São Paulo)`
5. Aguarde a criação do projeto (2-3 minutos)

#### 3.2 Configurar Banco de Dados

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New Query**
3. Copie e cole o conteúdo de `backend/schema.sql`
4. Clique em **Run**

#### 3.3 Configurar Storage

1. Vá em **Storage**
2. Clique em **Create a new bucket**
3. Nome: `modelos3d`
4. Marque **Public bucket**
5. Clique em **Create bucket**

#### 3.4 Obter Credenciais

1. Vá em **Settings** → **API**
2. Copie:
   - `URL` (SUPABASE_URL)
   - `anon public` key (SUPABASE_ANON_KEY)
   - `service_role` key (SUPABASE_SERVICE_KEY)

#### 3.5 Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
```

### 4. Instalar Meshroom

1. Baixe a versão mais recente:
   - https://github.com/alicevision/meshroom/releases
   - Arquivo: `Meshroom-2023.3.0-win64.zip`

2. Extraia para `C:\Program Files\Meshroom`

3. Teste a instalação:
   - Execute `Meshroom.exe`
   - A interface gráfica deve abrir

### 5. Instalar Blender

1. Baixe do site oficial:
   - https://www.blender.org/download/
   - Versão: Blender 4.0 LTS

2. Instale normalmente

3. Teste a instalação:
   ```bash
   blender --version
   ```

### 6. Instalar Python e Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar dependências
pip install supabase python-dotenv
```

## Configuração do Ambiente de Desenvolvimento

### 1. Estrutura de Pastas

```
project-imob/
├── frontend/           # Aplicação WebXR
│   ├── index.html      # Página principal
│   └── package.json    # Configuração Node
├── backend/            # Configuração Supabase
│   ├── schema.sql      # Schema do banco
│   └── edge_functions/ # Funções serverless
├── scripts/            # Scripts de processamento
│   ├── processar_fotos.py
│   └── captura_fotos.html
├── docs/               # Documentação
│   ├── ARQUITETURA.md
│   └── INSTALACAO.md
├── .gitignore          # Arquivos ignorados
└── README.md           # Documentação principal
```

### 2. Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key

# Caminhos (ajuste conforme instalação)
MESHROOM_PATH=C:\Program Files\Meshroom\Meshroom.exe
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
```

### 3. Testar a Instalação

#### Teste do Frontend
```bash
cd frontend
npx serve .
```
Acesse http://localhost:3000

#### Teste do Backend
```bash
python scripts/processar_fotos.py --help
```

#### Teste do Meshroom
Abra o Meshroom e crie um projeto novo.

## Configuração para Produção

### 1. Hospedagem do Frontend

Use o Vercel (gratuito):

```bash
npm i -g vercel
cd frontend
vercel
```

### 2. Hospedagem do Backend

O Supabase já está hospedado na nuvem. Configure:

1. **Domínio personalizado** (opcional)
2. **SSL/TLS** (automático)
3. **Backups** (automático no plano gratuito)

### 3. Processamento 3D

Para produção, considere:

- **Google Colab** para processamento gratuito
- **AWS EC2** com GPU para processamento em lote
- **Pipeline automatizado** com scripts Python

## Solução de Problemas

### Erro: "Meshroom não encontrado"
- Verifique se o caminho está correto em `.env`
- Instale o Meshroom em `C:\Program Files\Meshroom`

### Erro: "Blender não encontrado"
- Verifique se o caminho está correto em `.env`
- Instale o Blender em `C:\Program Files\Blender Foundation\Blender 4.0`

### Erro: "Supabase connection failed"
- Verifique se as credenciais estão corretas
- Confirme se o projeto está ativo no Supabase

### Erro: "Module not found"
- Ative o ambiente virtual: `venv\Scripts\activate`
- Instale dependências: `pip install -r requirements.txt`

## Recursos Adicionais

- [Documentação do Meshroom](https://meshroom.readthedocs.io)
- [Documentação do Blender](https://docs.blender.org)
- [Documentação do Supabase](https://supabase.com/docs)
- [Documentação do A-Frame](https://aframe.io/docs)

## Suporte

Para dúvidas ou problemas:
1. Verifique a documentação acima
2. Consulte os logs de erro
3. Abra uma issue no GitHub
