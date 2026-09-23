"""Executa os scripts no PostgreSQL e guarda, em resultados.json, o que o
documento mostra: o estado das tabelas depois de cada etapa da carga, as
consultas de verificação e as mensagens de erro dos testes de integridade.

    python coletar_resultados.py      # precisa de um PostgreSQL 16 local,
                                      # com o usuário do sistema como superusuário

Assim, toda saída reproduzida no documento veio de uma execução real.
"""
import json
import os
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
CRIAR = os.path.join(AQUI, '..', '01_criar_banco.sql')
CARGA = os.path.join(AQUI, '..', '02_tabelas_e_carga.sql')
PSQL = ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1']


def ler(caminho):
    return open(caminho, encoding='utf-8').read()


def executar(sql, banco='concessionaria_db', lote=False):
    cmd = PSQL + ['-d', banco]
    if lote:
        cmd += ['-A', '-F', '\t', '-P', 'footer=off', '-P', 'null=NULL']
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    return r.stdout, r.stderr.strip()


def recriar():
    # psql envia um comando por vez, então DROP e CREATE DATABASE funcionam
    r = subprocess.run(PSQL + ['-d', 'postgres', '-f', CRIAR], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)


def consulta(sql):
    saida, erro = executar(sql, lote=True)
    if erro:
        raise RuntimeError(erro)
    linhas = [l.split('\t') for l in saida.rstrip('\n').split('\n')]
    return {'colunas': linhas[0], 'linhas': linhas[1:]}


def carga_ate(marcador):
    """Arquivo 2 do início até a linha do marcador (exclusive)."""
    texto = ler(CARGA)
    return texto[:texto.index(marcador)]


def rodar(sql):
    recriar()
    _, erro = executar(sql)
    if erro:
        raise RuntimeError(erro)


SITUACAO = (
    "SELECT 'Onix' AS item, preco::text AS valor FROM veiculos WHERE modelo = 'Onix' "
    "UNION ALL SELECT 'Compass', status FROM veiculos WHERE placa = 'PQR6I78' "
    "UNION ALL SELECT 'Mariana', telefone FROM clientes WHERE cpf = '123.456.789-00' "
    "UNION ALL (SELECT nome, salario::text FROM funcionarios "
    "WHERE cargo = 'Vendedor' ORDER BY id)")

resultados = {}

# Etapa 1: estrutura + cadastros
rodar(carga_ate('-- 3.2)'))
resultados['apos_insert_veiculos'] = consulta('SELECT * FROM veiculos ORDER BY id')
resultados['antes_update'] = consulta(SITUACAO)

# Etapa 2: vendas
rodar(carga_ate('-- 3.3)'))
resultados['apos_vendas'] = consulta('SELECT * FROM vendas ORDER BY id')

# Etapa 3: atualizações
rodar(carga_ate('-- 3.4)'))
resultados['depois_update'] = consulta(SITUACAO)

# Script completo
rodar(ler(CARGA))

# Mesma consulta do Código 8 do documento
resultados['restricoes'] = consulta("""SELECT conrelid::regclass AS tabela,
       conname AS restricao,
       CASE contype WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'c' THEN 'CHECK'
                    WHEN 'f' THEN 'FOREIGN KEY' END AS tipo
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
  AND contype IN ('p', 'u', 'c', 'f')
ORDER BY conrelid::regclass::text, tipo, conname;""")

# As quatro consultas de verificação, exatamente como estão no script
texto = ler(CARGA)
bloco = texto[texto.index('-- 5) CONSULTAS'):]
comandos = [c.strip() for c in bloco.split(';') if 'SELECT' in c]
nomes = ['final_contagem', 'final_estoque', 'final_vendas', 'final_por_funcionario']
for nome, cmd in zip(nomes, comandos):
    sql = '\n'.join(l for l in cmd.split('\n') if not l.startswith('--'))
    resultados[nome] = consulta(sql)

# Testes de integridade: cada um deve falhar
testes = {
    'teste_fk': "DELETE FROM clientes WHERE cpf = '123.456.789-00';",
    'teste_unique': "INSERT INTO vendas (cliente_id, funcionario_id, veiculo_id, "
                    "data_venda, valor_venda) VALUES (3, 3, 1, '2026-09-21', 70000.00);",
    'teste_check': "UPDATE veiculos SET status = 'Vendida' WHERE id = 6;",
}
for nome, sql in testes.items():
    _, erro = executar(sql)
    assert erro.startswith('ERROR') or 'ERROR' in erro, (nome, erro)
    resultados[nome] = '\n'.join(l.replace('psql:<stdin>:1: ', '') for l in erro.split('\n'))

resultados['versao'] = consulta('SHOW server_version')['linhas'][0][0].split()[0]

with open(os.path.join(AQUI, 'resultados.json'), 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=1)
print('resultados.json gravado | PostgreSQL', resultados['versao'])
for k in ('antes_update', 'depois_update', 'teste_fk', 'teste_unique', 'teste_check', 'restricoes'):
    print(k, resultados[k])
