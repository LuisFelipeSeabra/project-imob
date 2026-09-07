import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Verificar autenticação
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Token de autenticação necessário' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 401 }
      )
    }

    const token = authHeader.replace('Bearer ', '')
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Verificar se token é válido
    const { data: { user }, error: authError } = await supabaseClient.auth.getUser(token)
    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Token inválido ou expirado' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 401 }
      )
    }

    const { imovelId, arquivo, nomeArquivo, tamanho, formato } = await req.json()

    // Validações
    if (!imovelId || !arquivo) {
      return new Response(
        JSON.stringify({ error: 'imovelId e arquivo são obrigatórios' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Validar formato do arquivo
    const extensoesPermitidas = ['.glb', '.gltf']
    const extensao = nomeArquivo?.toLowerCase().split('.').pop()
    if (!extensao || !extensoesPermitidas.includes('.' + extensao)) {
      return new Response(
        JSON.stringify({ error: 'Formato de arquivo inválido. Apenas .glb e .gltf são permitidos' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Validar tamanho máximo (50MB)
    const tamanhoMaximo = 50 * 1024 * 1024
    if (tamanho && tamanho > tamanhoMaximo) {
      return new Response(
        JSON.stringify({ error: 'Arquivo muito grande. Tamanho máximo: 50MB' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Verificar se o imóvel pertence ao usuário
    const { data: imovel, error: imovelError } = await supabaseClient
      .from('imoveis')
      .select('imobiliaria_id')
      .eq('id', imovelId)
      .single()

    if (imovelError || !imovel) {
      return new Response(
        JSON.stringify({ error: 'Imóvel não encontrado' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 }
      )
    }

    // Verificar se usuário tem permissão (é o dono da imobiliária)
    const { data: imobiliaria, error: imobiliariaError } = await supabaseClient
      .from('imobiliarias')
      .select('id')
      .eq('id', imovel.imobiliaria_id)
      .eq('id', user.id)
      .single()

    if (imobiliariaError || !imobiliaria) {
      return new Response(
        JSON.stringify({ error: 'Você não tem permissão para fazer upload neste imóvel' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 403 }
      )
    }

    // Sanitizar nome do arquivo
    const nomeFinal = nomeArquivo
      ? nomeArquivo.replace(/[^a-zA-Z0-9._-]/g, '_')
      : `modelo_${imovelId}.glb`

    const caminho = `modelos/${imovelId}/${nomeFinal}`

    // Upload do arquivo para Storage
    const { data: uploadData, error: uploadError } = await supabaseClient.storage
      .from('modelos3d')
      .upload(caminho, arquivo, {
        contentType: 'model/gltf-binary',
        upsert: true
      })

    if (uploadError) {
      throw uploadError
    }

    // Obter URL pública
    const { data: { publicUrl } } = supabaseClient.storage
      .from('modelos3d')
      .getPublicUrl(caminho)

    // Gerar hash do arquivo (simplificado)
    const hash = await crypto.subtle.digest('SHA-256', arquivo)
    const hashHex = Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')

    // Atualizar registro do imóvel
    const { error: updateError } = await supabaseClient
      .from('imoveis')
      .update({
        url_modelo_3d: publicUrl,
        status: 'pronto',
        tamanho_modelo: tamanho,
        formato_modelo: extensao,
        hash_modelo: hashHex,
        updated_at: new Date().toISOString()
      })
      .eq('id', imovelId)

    if (updateError) {
      throw updateError
    }

    // Registrar log
    await supabaseClient.from('logs').insert({
      nivel: 'info',
      acao: 'upload_modelo',
      tabela_afetada: 'imoveis',
      registro_id: imovelId,
      dados_novos: {
        url_modelo_3d: publicUrl,
        tamanho_modelo: tamanho,
        formato_modelo: extensao
      },
      usuario_id: user.id
    })

    return new Response(
      JSON.stringify({
        success: true,
        url: publicUrl,
        caminho: caminho,
        hash: hashHex
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})
