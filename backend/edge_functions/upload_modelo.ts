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
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { imovelId, arquivo, nomeArquivo } = await req.json()

    if (!imovelId || !arquivo) {
      return new Response(
        JSON.stringify({ error: 'imovelId e arquivo são obrigatórios' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Upload do arquivo para Storage
    const nomeFinal = nomeArquivo || `modelo_${imovelId}.glb`
    const caminho = `modelos/${imovelId}/${nomeFinal}`

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

    // Atualizar registro do imóvel
    const { error: updateError } = await supabaseClient
      .from('imoveis')
      .update({
        url_modelo_3d: publicUrl,
        status: 'pronto',
        updated_at: new Date().toISOString()
      })
      .eq('id', imovelId)

    if (updateError) {
      throw updateError
    }

    return new Response(
      JSON.stringify({
        success: true,
        url: publicUrl,
        caminho: caminho
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
