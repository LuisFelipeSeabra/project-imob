# 🗺️ Roadmap - Project Imob

Funcionalidades planejadas e prioridades de evolução do produto. Para o status do que já existe, veja [STATUS.md](STATUS.md).

---

## Prioridade Alta 🔴

### 1. Automação completa do pipeline
Hoje o processamento Meshroom via CLI é parcial (~70%). Evoluir para API interna do Meshroom ou workers dedicados com progresso real.

### 2. Validação de qualidade em tempo real
Analisar blur, exposição e sobreposição durante a captura em `scripts/captura_fotos.html`, orientando o usuário enquanto fotografa.

### 3. Sistema de cache de modelos
Expandir o cache de `frontend/otimizacao.js` para cache distribuído com versionamento por hash do modelo.

### 4. Notificações em tempo real
Usar Supabase Realtime para avisar quando um processamento concluir, sem polling.

---

## Prioridade Média 🟠

### 5. Decoração virtual com IA
Gerar variações de ambientação (Stable Diffusion ou similar) aplicadas como texturas sobre o modelo 3D. **Valor:** cliente visualiza o imóvel mobiliado; diferencial competitivo.

### 6. Comparador de imóveis
Visualização lado a lado de dois tours/dados. **Valor:** facilita decisão e aumenta engajamento.

### 7. Chat virtual integrado
Conversa em tempo real entre cliente e corretor dentro do tour. **Valor:** suporte instantâneo e maior confiança.

### 8. Analytics avançado
Mapa de calor de navegação no tour, tempo por cômodo, pontos de abandono.

---

## Prioridade Baixa 🟡

### 9. Agendamento de visitas
Agenda integrada com confirmação automática por e-mail/WhatsApp.

### 10. Simulador de financiamento
Calculadora de parcelas dentro da página do imóvel.

### 11. Edição colaborativa
Corretor e cliente movendo objetos/ajustando cores juntos na mesma sessão.

### 12. Plantas automáticas
Geração de planta baixa 2D a partir do modelo 3D.

### 13. Análise de mercado
Precificação sugerida com base em dados de mercado por região.

---

## Fases sugeridas

| Fase | Escopo | Duração estimada |
|------|--------|------------------|
| 1 - Fundação | Itens 1-4 (automação e qualidade) | 2 semanas |
| 2 - Experiência | Itens 5-8 (diferenciais de UX) | 2 semanas |
| 3 - Expansão | Itens 9-12 (ferramentas de venda) | 4 semanas |
| 4 - Inteligência | Item 13 + AR + multiplayer | 4 semanas |

---

## Impacto esperado

| Funcionalidade | Impacto | ROI estimado |
|----------------|---------|--------------|
| Decoração virtual | Alto | +40% conversão |
| Chat virtual | Alto | +30% satisfação |
| Simulador | Alto | +35% fechamento |
| Comparador | Médio | +25% engajamento |
| Agendamento | Médio | +20% eficiência |
| Edição colaborativa | Médio | +15% tempo no site |
| Análise de mercado | Médio | +20% precificação |
| Plantas automáticas | Baixo | +10% confiança |

---

> Estimativas de ROI são projeções de produto, não medições — validar com dados reais após implementação.
