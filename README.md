# Project Imob

🚀 **Startup de Realidade Virtual para Imobiliárias**

Plataforma que permite a criação de tours virtuais em realidade virtual (VR) de imóveis a partir de fotos capturadas com smartphone.

## 📋 Objetivo

Permitir que clientes de imobiliárias visualizem terrenos, casas e decorações em realidade virtual, melhorando a experiência de compra e reduzindo a necessidade de visitas físicas.

## 🎯 Funcionalidades

- ✅ Captura de fotos com smartphone
- ✅ Processamento 3D com Meshroom (fotogrametria)
- ✅ Otimização de modelos com Blender
- ✅ Visualização WebXR em qualquer navegador
- ✅ Suporte a VR (Meta Quest, Cardboard)
- ✅ Painel administrativo para imobiliárias
- ✅ Analytics de visualizações

## 🏗️ Arquitetura

```
📸 Fotos → 🔄 Processamento 3D → ☁️ Supabase → 🌐 WebXR → 👓 VR
```

## 📁 Estrutura do Projeto

```
project-imob/
├── frontend/              # Aplicação WebXR (A-Frame + Three.js)
│   ├── index.html         # Tour virtual principal
│   └── package.json       # Configuração Node.js
├── backend/               # Backend Supabase
│   ├── schema.sql         # Schema do banco de dados
│   ├── supabase_config.toml
│   └── edge_functions/    # Funções serverless
├── scripts/               # Scripts de processamento
│   ├── processar_fotos.py # Pipeline 3D
│   └── captura_fotos.html # Interface de captura
├── docs/                  # Documentação técnica
│   ├── ARQUITETURA.md     # Diagrama e componentes
│   └── INSTALACAO.md      # Guia de instalação
├── .gitignore             # Arquivos ignorados
└── README.md              # Este arquivo
```

## 🚀 Tecnologias

### Frontend
- **A-Frame**: Framework WebXR para VR
- **Three.js**: Renderização 3D
- **HTML5/CSS3**: Interface do usuário

### Backend
- **Supabase**: Banco de dados, auth, storage
- **PostgreSQL**: Banco relacional
- **Edge Functions**: Processamento serverless

### Processamento 3D
- **Meshroom**: Fotogrametria (reconstrução 3D)
- **Blender**: Otimização e exportação
- **Python**: Scripts de automação

### Hospedagem
- **Vercel**: Frontend e preview
- **Supabase**: Backend e storage

## 📦 Instalação

### Pré-requisitos

- Windows 10/11
- Python 3.8+
- GPU NVIDIA (recomendado)
- 16GB RAM

### Passo a Passo

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/LuisFelipeSeabra/project-imob.git
   cd project-imob
   ```

2. **Configurar Supabase**
   - Criar projeto em https://supabase.com
   - Executar `backend/schema.sql`
   - Configurar storage bucket `modelos3d`

3. **Instalar Meshroom**
   - Baixar de https://github.com/alicevision/meshroom
   - Extrair para `C:\Program Files\Meshroom`

4. **Instalar Blender**
   - Baixar de https://www.blender.org
   - Instalar normalmente

5. **Configurar variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Editar .env com suas credenciais
   ```

6. **Testar o frontend**
   ```bash
   cd frontend
   npx serve .
   ```

## 📖 Documentação

- [Arquitetura do Sistema](docs/ARQUITETURA.md)
- [Guia de Instalação](docs/INSTALACAO.md)

## 🎮 Como Usar

### Para Imobiliárias

1. **Capturar fotos** do imóvel com smartphone
2. **Processar** com Meshroom e Blender
3. **Fazer upload** para o Supabase
4. **Compartilhar** link do tour com clientes

### Para Clientes

1. Acessar o link do tour
2. Navegar com mouse ou touch
3. Ativar modo VR (se disponível)
4. Explorar o imóvel livremente

## 🛠️ Scripts Disponíveis

### Processamento de Fotos

```bash
python scripts/processar_fotos.py <diretorio_fotos> <imovel_id>
```

### Captura de Fotos

Abra `scripts/captura_fotos.html` no navegador do smartphone.

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key

# Caminhos (Windows)
MESHROOM_PATH=C:\Program Files\Meshroom\Meshroom.exe
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
```

## 📊 Banco de Dados

### Tabelas Principais

- **imobiliarias**: Cadastro de imobiliárias
- **imoveis**: Dados dos imóveis
- **fotos_captura**: Fotos brutas
- **clientes**: Leads/clientes
- **visualizacoes**: Analytics de uso
- **favoritos**: Imóveis favoritados

## 🎨 Personalização

### Cores e Temas

Edite `frontend/index.html`:

```css
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --background-color: #f8f9fa;
}
```

### Controles

Modifique os controles do A-Frame para atender às necessidades:

```html
<a-camera
  look-controls="pointerLockEnabled: true"
  wasd-controls="acceleration: 20"
></a-camera>
```

## 🔒 Segurança

- **Row Level Security (RLS)**: Isolamento de dados por imobiliária
- **JWT Authentication**: Autenticação segura via Supabase
- **Storage Privado**: URLs assinadas para modelos 3D
- **HTTPS**: Comunicação criptografada

## 📈 Roadmap

### Fase 1 (Atual)
- [x] Estrutura básica do projeto
- [x] Frontend WebXR
- [x] Backend Supabase
- [x] Scripts de processamento

### Fase 2 (Próximos passos)
- [ ] Pipeline automatizado de processamento
- [ ] App nativo (Unity/Godot)
- [ ] IA para decoração virtual
- [ ] Integração com pagamento

### Fase 3 (Futuro)
- [ ] NeRF/Gaussian Splatting
- [ ] Realidade aumentada
- [ ] Multiplayer para visitas em grupo
- [ ] Marketplace de decoração

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Luis Felipe Seabra**
- GitHub: [@LuisFelipeSeabra](https://github.com/LuisFelipeSeabra)
- Email: felipeseabra2405@gmail.com

## 🙏 Agradecimentos

- Comunidade open-source
- AliceVision (Meshroom)
- Supabase
- A-Frame e Three.js

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
