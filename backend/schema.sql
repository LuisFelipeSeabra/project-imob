-- Schema inicial para o banco de dados do Project Imob
-- Execute no SQL Editor do Supabase

-- Extensão para UUIDs
create extension if not exists "uuid-ossp";

-- Tabela de imobiliárias
create table imobiliarias (
  id uuid default gen_random_uuid() primary key,
  nome text not null,
  cnpj text,
  email text unique not null,
  telefone text,
  endereco text,
  logo_url text,
  plano text default 'free',
  status text default 'ativo',
  created_at timestamp default now(),
  updated_at timestamp default now()
);

-- Tabela de imóveis
create table imoveis (
  id uuid default gen_random_uuid() primary key,
  imobiliaria_id uuid references imobiliarias(id) on delete cascade,
  titulo text not null,
  descricao text,
  tipo text not null check (tipo in ('casa', 'apartamento', 'terreno', 'comercial')),
  area_m2 numeric,
  quartos integer,
  banheiros integer,
  vagas integer,
  preco numeric,
  endereco jsonb,
  url_modelo_3d text,
  url_fotos jsonb,
  url_tour_360 text,
  status text default 'processando',
  destaque boolean default false,
  views integer default 0,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

-- Tabela de fotos brutas
create table fotos_captura (
  id uuid default gen_random_uuid() primary key,
  imovel_id uuid references imoveis(id) on delete cascade,
  nome_arquivo text,
  url_foto text not null,
  metadata jsonb,
  processada boolean default false,
  created_at timestamp default now()
);

-- Tabela de clientes/leads
create table clientes (
  id uuid default gen_random_uuid() primary key,
  imobiliaria_id uuid references imobiliarias(id) on delete cascade,
  nome text not null,
  email text,
  telefone text,
  origem text,
  created_at timestamp default now()
);

-- Tabela de visualizações
create table visualizacoes (
  id uuid default gen_random_uuid() primary key,
  imovel_id uuid references imoveis(id) on delete cascade,
  cliente_id uuid references clientes(id),
  session_id text,
  tempo_segundos integer,
  dispositivo text,
  tipo_visita text check (tipo_visita in ('2d', 'vr', '360')),
  interacoes jsonb,
  created_at timestamp default now()
);

-- Tabela de favoritos
create table favoritos (
  id uuid default gen_random_uuid() primary key,
  cliente_id uuid references clientes(id) on delete cascade,
  imovel_id uuid references imoveis(id) on delete cascade,
  created_at timestamp default now(),
  unique(cliente_id, imovel_id)
);

-- Índices para performance
create index idx_imoveis_imobiliaria on imoveis(imobiliaria_id);
create index idx_imoveis_status on imoveis(status);
create index idx_imoveis_destaque on imoveis(destaque);
create index idx_visualizacoes_imovel on visualizacoes(imovel_id);
create index idx_visualizacoes_cliente on visualizacoes(cliente_id);
create index idx_fotos_imovel on fotos_captura(imovel_id);

-- Triggers para updated_at
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger imobiliarias_updated_at
  before update on imobiliarias
  for each row execute procedure update_updated_at();

create trigger imoveis_updated_at
  before update on imoveis
  for each row execute procedure update_updated_at();

-- Função para incrementar visualizações
create or replace function incrementar_views(imovel_id uuid)
returns void as $$
begin
  update imoveis
  set views = views + 1
  where id = imovel_id;
end;
$$ language plpgsql;

-- Políticas de segurança RLS (Row Level Security)
-- Habilitar RLS em todas as tabelas
alter table imobiliarias enable row level security;
alter table imoveis enable row level security;
alter table fotos_captura enable row level security;
alter table clientes enable row level security;
alter table visualizacoes enable row level security;
alter table favoritos enable row level security;

-- Políticas: usuários só veem dados de suas imobiliárias
create policy "Imobiliárias veem seus dados" on imobiliarias
  for all using (auth.uid() = id);

create policy "Imóveis públicos para leitura" on imoveis
  for select using (status = 'pronto');

create policy "Imobiliárias gerenciam seus imóveis" on imoveis
  for all using (imobiliaria_id in (
    select id from imobiliarias where id = auth.uid()
  ));

create policy "Imobiliárias veem suas fotos" on fotos_captura
  for all using (imovel_id in (
    select id from imoveis where imobiliaria_id = auth.uid()
  ));

create policy "Clientes podem ser criados" on clientes
  for insert with check (true);

create policy "Imobiliárias veem seus clientes" on clientes
  for select using (imobiliaria_id = auth.uid());

create policy "Visualizações podem ser criadas" on visualizacoes
  for insert with check (true);

create policy "Imobiliárias veem visualizações de seus imóveis" on visualizacoes
  for select using (imovel_id in (
    select id from imoveis where imobiliaria_id = auth.uid()
  ));

create policy "Favoritos do cliente" on favoritos
  for all using (cliente_id = auth.uid());
