# Project Imob

Plataforma de tours virtuais em realidade virtual (VR) para imobiliárias, gerados a partir de fotos capturadas com smartphone.

**Versão:** 1.0.0 · **Status:** MVP funcional (78%) · **Licença:** MIT

---

## Início rápido

```bash
git clone https://github.com/LuisFelipeSeabra/project-imob.git
cd project-imob
pip install -r requirements.txt
```

Configure o Supabase (schema + buckets `modelos3d` e `fotos-captura`) e rode o frontend:

```bash
cd frontend && npx serve .
```

O passo a passo completo, incluindo Meshroom e Blender, está em [docs/INSTALACAO.md](docs/INSTALACAO.md).

---

## Documentação

| Documento | Quando consultar |
|-----------|------------------|
| [INSTALACAO.md](docs/INSTALACAO.md) | Instalar, configurar e rodar o projeto |
| [ARQUITETURA.md](docs/ARQUITETURA.md) | Entender componentes, fluxo de dados e stack |
| [STATUS.md](docs/STATUS.md) | Ver o que está implementado e o que falta |
| [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | Consumir a API (endpoints, modelos, erros) |
| [TUTORIAL_TESTES.md](docs/TUTORIAL_TESTES.md) | Executar testes e medir cobertura |
| [EXPLICACAO_CODIGO.md](docs/EXPLICACAO_CODIGO.md) | Navegar pelo código fonte |
| [ROADMAP.md](docs/ROADMAP.md) | Próximas funcionalidades e prioridades |

---

## Estrutura do projeto

```
project-imob/
├── frontend/                    # Aplicação WebXR
│   ├── index.html               # Tour virtual
│   └── otimizacao.js            # LOD, cache e compressão
├── backend/                     # Supabase
│   ├── schema.sql               # Schema do banco
│   └── edge_functions/          # Funções serverless
├── scripts/                     # Processamento
│   ├── captura_fotos.html       # Captura via smartphone
│   ├── processar_fotos.py       # Pipeline Meshroom + Blender
│   ├── fila_processamento.py    # Fila assíncrona de jobs
│   └── iniciar_fila.bat         # Inicialização (Windows)
├── tests/                       # Testes unitários
├── docs/                        # Documentação
└── .github/workflows/ci.yml     # CI/CD
```

---

## Fluxo de uso

**Imobiliária:** captura fotos em `scripts/captura_fotos.html` → o sistema processa via fila → compartilha o link do tour.

**Cliente:** abre o link → navega com mouse ou toque → ativa o modo VR se disponível.

---

## Comandos principais

```bash
# Processar fotos de um imóvel
python scripts/processar_fotos.py <diretorio_fotos> <imovel_id>

# Iniciar a fila de processamento
scripts\iniciar_fila.bat

# Rodar os testes
pytest tests/ -v
```

---

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Abra um Pull Request

---

## Autor

**Luis Felipe Seabra** — [@LuisFelipeSeabra](https://github.com/LuisFelipeSeabra) · felipeseabra2405@gmail.com
