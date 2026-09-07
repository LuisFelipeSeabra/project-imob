# 📡 Documentação da API - Project Imob

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints](#endpoints)
4. [Modelos de Dados](#modelos-de-dados)
5. [Códigos de Status](#códigos-de-status)
6. [Exemplos de Uso](#exemplos-de-uso)
7. [Rate Limiting](#rate-limiting)
8. [Versionamento](#versionamento)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A API do Project Imob permite gerenciar imóveis, processar fotos e gerar modelos 3D para tours virtuais.

### Base URL

```
https://seu-projeto.supabase.co
```

### Versão

```
v1
```

### Formato

```
Content-Type: application/json
```

---

## 🔐 Autenticação

### JWT Token

A API usa autenticação JWT via Supabase Auth.

#### Obter Token

```bash
curl -X POST 'https://seu-projeto.supabase.co/auth/v1/token?grant_type=password' \
  -H 'apikey: sua-anon-key' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "seu@email.com",
    "password": "sua-senha"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": {
    "id": "user-id",
    "email": "seu@email.com"
  }
}
```

#### Usar Token

```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/imoveis' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

## 📚 Endpoints

### 1. **Imóveis**

#### Listar Imóveis

```http
GET /rest/v1/imoveis
```

**Parâmetros:**
- `select` - Campos a retornar (opcional)
- `status` - Filtrar por status (opcional)
- `tipo` - Filtrar por tipo (opcional)
- `destaque` - Filtrar por destaque (opcional)
- `limit` - Limite de resultados (padrão: 20)
- `offset` - Offset para paginação (padrão: 0)

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/imoveis?select=id,titulo,preco&status=pronto&limit=10' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

**Resposta:**
```json
[
  {
    "id": "imovel-123",
    "titulo": "Apartamento 3 quartos",
    "preco": 350000,
    "status": "pronto",
    "tipo": "apartamento",
    "area_m2": 120
  }
]
```

#### Buscar Imóvel por ID

```http
GET /rest/v1/imoveis/{id}
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/imoveis/imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

**Resposta:**
```json
{
  "id": "imovel-123",
  "titulo": "Apartamento 3 quartos",
  "descricao": "Apartamento com 3 quartos, 2 banheiros",
  "tipo": "apartamento",
  "area_m2": 120,
  "quartos": 3,
  "banheiros": 2,
  "preco": 350000,
  "status": "pronto",
  "url_modelo_3d": "https://...",
  "created_at": "2026-09-07T17:00:00Z"
}
```

#### Criar Imóvel

```http
POST /rest/v1/imoveis
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/imoveis' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "titulo": "Casa 4 quartos",
    "descricao": "Casa com 4 quartos, 3 banheiros",
    "tipo": "casa",
    "area_m2": 200,
    "quartos": 4,
    "banheiros": 3,
    "preco": 500000
  }'
```

#### Atualizar Imóvel

```http
PATCH /rest/v1/imoveis/{id}
```

**Exemplo:**
```bash
curl -X PATCH 'https://seu-projeto.supabase.co/rest/v1/imoveis/imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "preco": 380000,
    "status": "pronto"
  }'
```

#### Deletar Imóvel

```http
DELETE /rest/v1/imoveis/{id}
```

**Exemplo:**
```bash
curl -X DELETE 'https://seu-projeto.supabase.co/rest/v1/imoveis/imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

### 2. **Fotos**

#### Upload de Foto

```http
POST /storage/v1/object/fotos-captura/{imovel_id}/{nome_arquivo}
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/storage/v1/object/fotos-captura/imovel-123/foto_001.jpg' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: image/jpeg' \
  --data-binary '@foto_001.jpg'
```

#### Listar Fotos de um Imóvel

```http
GET /rest/v1/fotos_captura?imovel_id=eq.{imovel_id}
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/fotos_captura?imovel_id=eq.imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

### 3. **Processamento**

#### Criar Job de Processamento

```http
POST /rest/v1/processamento
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/processamento' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "imovel_id": "imovel-123",
    "tipo": "fotos",
    "status": "pendente"
  }'
```

#### Buscar Status de Processamento

```http
GET /rest/v1/processamento?imovel_id=eq.{imovel_id}
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/processamento?imovel_id=eq.imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

### 4. **Modelos 3D**

#### Upload de Modelo 3D

```http
POST /functions/v1/upload_modelo
```

**Headers:**
```
Authorization: Bearer seu-token-jwt
Content-Type: application/json
```

**Body:**
```json
{
  "imovelId": "imovel-123",
  "arquivo": "base64_encoded_file",
  "nomeArquivo": "modelo.glb",
  "tamanho": 1024000,
  "formato": "glb"
}
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/functions/v1/upload_modelo' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "imovelId": "imovel-123",
    "arquivo": "base64_encoded_file",
    "nomeArquivo": "modelo.glb",
    "tamanho": 1024000,
    "formato": "glb"
  }'
```

**Resposta:**
```json
{
  "success": true,
  "url": "https://seu-projeto.supabase.co/storage/v1/object/public/modelos3d/imovel-123/modelo.glb",
  "caminho": "modelos/imovel-123/modelo.glb",
  "hash": "a1b2c3d4e5f6..."
}
```

#### Download de Modelo 3D

```http
GET /storage/v1/object/public/modelos3d/{imovel_id}/{nome_arquivo}
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/storage/v1/object/public/modelos3d/imovel-123/modelo.glb' \
  -H 'apikey: sua-anon-key' \
  -o modelo.glb
```

---

### 5. **Clientes**

#### Listar Clientes

```http
GET /rest/v1/clientes
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/clientes' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

#### Criar Cliente

```http
POST /rest/v1/clientes
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/clientes' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "João Silva",
    "email": "joao@email.com",
    "telefone": "11999999999"
  }'
```

---

### 6. **Visualizações**

#### Registrar Visualização

```http
POST /rest/v1/visualizacoes
```

**Exemplo:**
```bash
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/visualizacoes' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "imovel_id": "imovel-123",
    "cliente_id": "cliente-456",
    "session_id": "sess-789",
    "tempo_segundos": 300,
    "dispositivo": "desktop",
    "tipo_visita": "vr"
  }'
```

#### Buscar Visualizações de um Imóvel

```http
GET /rest/v1/visualizacoes?imovel_id=eq.{imovel_id}
```

**Exemplo:**
```bash
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/visualizacoes?imovel_id=eq.imovel-123' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

## 📊 Modelos de Dados

### Imóvel

```json
{
  "id": "uuid",
  "imobiliaria_id": "uuid",
  "titulo": "string",
  "descricao": "string",
  "tipo": "casa|apartamento|terreno|comercial",
  "area_m2": "number",
  "quartos": "integer",
  "banheiros": "integer",
  "vagas": "integer",
  "preco": "number",
  "endereco": {
    "rua": "string",
    "numero": "string",
    "bairro": "string",
    "cidade": "string",
    "estado": "string",
    "cep": "string"
  },
  "url_modelo_3d": "string",
  "url_fotos": ["string"],
  "url_tour_360": "string",
  "status": "processando|pronto|erro",
  "destaque": "boolean",
  "views": "integer",
  "tamanho_modelo": "integer",
  "formato_modelo": "string",
  "hash_modelo": "string",
  "metadados": "object",
  "versao": "integer",
  "deleted_at": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Foto de Captura

```json
{
  "id": "uuid",
  "imovel_id": "uuid",
  "nome_arquivo": "string",
  "url_foto": "string",
  "metadata": "object",
  "processada": "boolean",
  "created_at": "timestamp"
}
```

### Processamento

```json
{
  "id": "uuid",
  "imovel_id": "uuid",
  "tipo": "fotos|modelo_3d|tour_360",
  "status": "pendente|processando|concluido|erro",
  "progresso": "integer",
  "input_data": "object",
  "output_data": "object",
  "erro_mensagem": "string",
  "tentativas": "integer",
  "max_tentativas": "integer",
  "started_at": "timestamp",
  "finished_at": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Cliente

```json
{
  "id": "uuid",
  "imobiliaria_id": "uuid",
  "nome": "string",
  "email": "string",
  "telefone": "string",
  "origem": "string",
  "created_at": "timestamp"
}
```

### Visualização

```json
{
  "id": "uuid",
  "imovel_id": "uuid",
  "cliente_id": "uuid",
  "session_id": "string",
  "tempo_segundos": "integer",
  "dispositivo": "string",
  "tipo_visita": "2d|vr|360",
  "interacoes": "object",
  "created_at": "timestamp"
}
```

---

## 📋 Códigos de Status

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 403 | Proibido |
| 404 | Não encontrado |
| 409 | Conflito |
| 429 | Muitas requisições |
| 500 | Erro interno do servidor |

---

## 💡 Exemplos de Uso

### Fluxo Completo: Capturar → Processar → Visualizar

```bash
# 1. Criar imóvel
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/imoveis' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "titulo": "Casa 3 quartos",
    "tipo": "casa",
    "area_m2": 150,
    "quartos": 3,
    "preco": 400000
  }'

# 2. Upload de fotos
curl -X POST 'https://seu-projeto.supabase.co/storage/v1/object/fotos-captura/imovel-123/foto_001.jpg' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: image/jpeg' \
  --data-binary '@foto_001.jpg'

# 3. Criar job de processamento
curl -X POST 'https://seu-projeto.supabase.co/rest/v1/processamento' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "imovel_id": "imovel-123",
    "tipo": "fotos",
    "status": "pendente"
  }'

# 4. Upload de modelo 3D
curl -X POST 'https://seu-projeto.supabase.co/functions/v1/upload_modelo' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt' \
  -H 'Content-Type: application/json' \
  -d '{
    "imovelId": "imovel-123",
    "arquivo": "base64_encoded_file",
    "nomeArquivo": "modelo.glb"
  }'

# 5. Visualizar tour
# Acesse: https://seu-projeto.supabase.co/frontend/index.html?id=imovel-123
```

---

## ⚡ Rate Limiting

### Limites

| Endpoint | Limite | Janela |
|----------|--------|--------|
| Autenticação | 5 req | 1 min |
| Upload | 10 req | 1 min |
| Leitura | 100 req | 1 min |
| Escrita | 50 req | 1 min |

### Headers de Rate Limit

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1630000000
```

---

## 🔄 Versionamento

### Versão Atual

```
v1
```

### Endpoints por Versão

- **v1** - Versão atual (produção)
- **v0** - Versão legada (deprecada)

### Cabeçalho de Versão

```http
Accept: application/vnd.project-imob.v1+json
```

---

## 🐛 Troubleshooting

### Erros Comuns

#### 1. **401 Unauthorized**
```json
{
  "error": "Token de autenticação necessário"
}
```
**Solução:** Verifique se o token está correto e não expirou.

#### 2. **403 Forbidden**
```json
{
  "error": "Você não tem permissão para acessar este recurso"
}
```
**Solução:** Verifique se você tem permissão para acessar o recurso.

#### 3. **404 Not Found**
```json
{
  "error": "Recurso não encontrado"
}
```
**Solução:** Verifique se o ID do recurso está correto.

#### 4. **429 Too Many Requests**
```json
{
  "error": "Muitas requisições. Tente novamente em alguns segundos."
}
```
**Solução:** Aguarde alguns segundos e tente novamente.

#### 5. **500 Internal Server Error**
```json
{
  "error": "Erro interno do servidor"
}
```
**Solução:** Contate o suporte ou verifique os logs.

### Logs de Debug

```bash
# Verificar logs do Supabase
curl -X GET 'https://seu-projeto.supabase.co/rest/v1/logs' \
  -H 'apikey: sua-anon-key' \
  -H 'Authorization: Bearer seu-token-jwt'
```

---

## 📚 Recursos Adicionais

- [Documentação do Supabase](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Postman Collection](https://www.postman.com/)

---

## 📞 Suporte

Para dúvidas sobre a API:

1. **Verifique os logs** em `fila_processamento.log`
2. **Consulte a documentação** em `docs/`
3. **Abra uma issue** no GitHub
4. **Contate o suporte** em suporte@project-imob.com

---

**Status:** ✅ Documentação completa da API implementada.