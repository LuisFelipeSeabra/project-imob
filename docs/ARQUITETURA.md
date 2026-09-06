# Arquitetura do Sistema - Project Imob

## Visão Geral

O Project Imob é uma plataforma que permite a imobiliárias criar tours virtuais em realidade virtual (VR) de imóveis a partir de fotos capturadas com smartphone.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMADA DE CAPTURA                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Smartphone   │  │  Câmera 360° │  │    Drone     │          │
│  │  (App Web)   │  │  (Opcional)  │  │  (Futuro)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                    Fotos (JPG/PNG)                               │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      CAMADA DE PROCESSAMENTO                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Meshroom   │  │   COLMAP     │  │   Nerfstudio │          │
│  │ (Fotogrametria)│  │ (Reconstrução)│  │   (NeRF)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                    Modelo 3D (OBJ/PLY)                           │
│                            │                                     │
│                    ┌───────▼───────┐                             │
│                    │    Blender    │                             │
│                    │  (Otimização) │                             │
│                    └───────┬───────┘                             │
│                            │                                     │
│                    Modelo Otimizado (.glb)                       │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                        CAMADA DE DADOS                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Supabase                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │  PostgreSQL  │  │   Storage    │  │  Edge Funcs  │   │   │
│  │  │  (Tabelas)   │  │  (Imagens/   │  │  (Upload)    │   │   │
│  │  │              │  │   Modelos)   │  │              │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      CAMADA DE APLICAÇÃO                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   A-Frame    │  │   Three.js   │  │   WebXR API  │          │
│  │  (Frontend)  │  │  (Render)    │  │  (VR/AR)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────┐           │
│  │              Navegador Web (Mobile/Desktop)        │           │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │           │
│  │  │  2D/3D   │  │  Cardboard│  │  Meta    │       │           │
│  │  │  Tour    │  │   Mode    │  │  Quest   │       │           │
│  │  └──────────┘  └──────────┘  └──────────┘       │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Frontend (WebXR)
- **Framework**: A-Frame + Three.js
- **Funcionalidades**:
  - Visualização 3D de imóveis
  - Navegação em primeira pessoa
  - Modo VR (Meta Quest, Cardboard)
  - Controles de toque e mouse
  - Informações do imóvel sobrepostas

### 2. Backend (Supabase)
- **Banco de Dados**: PostgreSQL
- **Storage**: Armazenamento de modelos 3D e fotos
- **Auth**: Autenticação de imobiliárias
- **Edge Functions**: Processamento de upload

### 3. Processamento 3D
- **Fotogrametria**: Meshroom (AliceVision)
- **Otimização**: Blender
- **Formato**: glTF/GLB (padrão web)

## Fluxo de Dados

1. **Captura**: Corretor fotografa o imóvel
2. **Upload**: Fotos são enviadas para processamento
3. **Reconstrução**: Meshroom gera modelo 3D
4. **Otimização**: Blender reduz polígonos e otimiza texturas
5. **Publicação**: Modelo é enviado para Supabase Storage
6. **Visualização**: Cliente acessa link e vê tour em VR

## Tecnologias

| Componente | Tecnologia | Licença |
|------------|------------|---------|
| Frontend | A-Frame, Three.js | MIT |
| Backend | Supabase | Apache 2.0 |
| Fotogrametria | Meshroom, COLMAP | MPL 2.0 / GPL |
| 3D | Blender | GPL |
| Banco de Dados | PostgreSQL | PostgreSQL |
| Storage | Supabase Storage | Apache 2.0 |
| Hospedagem | Vercel | - |

## Escalabilidade

### Fase 1 (MVP)
- Processamento manual
- Armazenamento local + Supabase
- Visualização web simples

### Fase 2 (Crescimento)
- Pipeline automatizado
- Edge Functions para processamento
- CDN para modelos

### Fase 3 (Escala)
- Processamento em cloud GPU
- Cache de modelos
- App nativo (Unity/Godot)

## Segurança

- **RLS (Row Level Security)**: Isolamento de dados por imobiliária
- **Autenticação**: JWT via Supabase Auth
- **Storage**: URLs assinadas para acesso temporário
- **HTTPS**: Comunicação criptografada

## Limitações Atuais

- Processamento 3D manual (não em tempo real)
- Requer GPU local para Meshroom
- Qualidade depende da captura de fotos
- Sem processamento em nuvem (gratuito)
