# Trabalho de Banco de Dados: Concessionária de Veículos

Implementação básica do banco de dados de uma concessionária em **PostgreSQL 16**,
para a disciplina de Laboratório de Banco de Dados da Faculdade Insted, seguindo as
orientações do professor Odirley Franco (entrega em 24/09, até as 19 h).

| Arquivo | O que é |
|---|---|
| `Documentacao_Concessionaria_ABNT.docx` | **A documentação de entrega**, no padrão ABNT (NBR 14724) |
| `Documentacao_Concessionaria_ABNT.pdf` | A mesma documentação em PDF, para conferir |
| `01_criar_banco.sql` | Script 1: cria o banco `concessionaria_db` |
| `02_tabelas_e_carga.sql` | Script 2: cria as tabelas e faz a carga (INSERT, UPDATE, DELETE) |
| `diagramas/mer.png`, `diagramas/der.png` | MER (conceitual, notação de Chen) e DER (lógico, pé de galinha) |
| `fontes/` | Os scripts que geram os diagramas e o `.docx`, e a saída real da execução no PostgreSQL |

A **apresentação** foi publicada como deck em
<https://claude.ai/artifact/W3iH8CZToEwpJy1QJDPsxA> (19 slides com notas do
apresentador; dá para baixar em PowerPoint ou PDF pelo próprio deck).

## O que o professor pediu e onde está

| Pedido | Onde está na documentação |
|---|---|
| Introdução e objetivo | Seções 1 e 2 |
| Escolha do banco de dados (1ª etapa: definir o SGBD) | Seção 3, com o Quadro 1 comparando PostgreSQL, MySQL e SQL Server |
| MER | Seção 4.2, Figura 1 |
| DER | Seção 4.3, Figura 2 |
| Dicionário de dados | Seção 4.4, Quadros 5 a 9 |
| Explicação da implementação: criar o database (2ª etapa) | Seção 5.1 |
| Criar a estrutura de tabelas (3ª etapa) | Seção 5.2 |
| Carga de dados com INSERT, UPDATE e DELETE (4ª etapa) | Seção 5.3, com o estado das tabelas antes e depois |
| Comandos utilizados | Seção 5 inteira, Quadro 19 (resumo) e Apêndices A e B (scripts completos) |
| Conclusão e referências | Seção 6 e Referências |

## Dados da capa

- **Instituição:** Faculdade Insted
- **Curso:** Análise e Desenvolvimento de Sistemas
- **Disciplina:** Laboratório de Banco de Dados
- **Professor:** Odirley Franco
- **Integrantes:**
  - João Victor Muller Miranda
  - Juliano dos Santos Apolinario Araujo
  - Júlio César Zadi de Assis dos Santos
  - Luan Flores Martins
- **Local e ano:** Campo Grande, 2026

O sumário e as listas de figuras, quadros e códigos já vêm com os números de
página preenchidos. Se o grupo mudar o texto a ponto de empurrar páginas,
confira os números antes de entregar.

## O que mudou em relação ao que o grupo já tinha

O modelo do grupo foi mantido: as mesmas 5 tabelas e colunas, e todos os
registros originais continuam nos scripts, com os mesmos ids. O que mudou:

1. **SGBD trocado de MySQL para PostgreSQL 16**, com os ajustes de sintaxe:
   - `GENERATED ALWAYS AS IDENTITY` no lugar de `AUTO_INCREMENT`;
   - `NUMERIC` no lugar de `DECIMAL`;
   - `SMALLINT` com CHECK no lugar de `YEAR`, que não existe no PostgreSQL;
   - `BEGIN` no lugar de `START TRANSACTION`;
   - `||` no lugar de `CONCAT`;
   - sem `ENGINE`, `SET NAMES` e `USE`.
2. **Dois scripts em vez de um**: no PostgreSQL não existe `USE`, então o banco é
   criado conectado ao `postgres`, e as tabelas, conectadas ao `concessionaria_db`.
3. **Scripts reexecutáveis**: `DROP DATABASE IF EXISTS` no início do script 1.
4. **Restrições CHECK**: situação do veículo só pode ser `Disponivel`, `Reservado` ou
   `Vendido`; preço, salário e valor da venda maiores que zero; ano entre 1900 e 2100.
5. **Restrições com nome** (`fk_venda_cliente`, `uq_venda_veiculo`...), o que deixa as
   mensagens de erro legíveis.
6. **Mais dados de exemplo**: 3 fornecedores, 7 veículos (um 0 km sem placa, para mostrar
   o NULL), 4 clientes, 3 funcionários e 3 vendas.
7. **Vendas em transação**: cada venda faz o INSERT em `vendas` e o UPDATE da situação do
   veículo entre `BEGIN` e `COMMIT`.
8. **Testes de integridade** (comentados no script 2): excluir cliente com venda, vender o
   mesmo veículo duas vezes e gravar uma situação inválida. Os três são recusados.
9. **Consultas de verificação** novas: contagem por tabela, estoque com `LEFT JOIN` e
   total vendido por funcionário com `GROUP BY`.

## Como rodar os scripts

**pgAdmin:**

1. Abra o Query Tool no banco `postgres` e abra `01_criar_banco.sql`. Selecione o
   `DROP DATABASE...` e tecle F5; depois selecione o `CREATE DATABASE...` e tecle F5.
   Um de cada vez, porque o PostgreSQL não aceita os dois juntos no mesmo bloco.
2. Atualize a lista de bancos (botão direito em *Databases* → *Refresh*), abra o Query
   Tool no `concessionaria_db`, abra `02_tabelas_e_carga.sql` e tecle F5.

**Terminal:**

```bash
psql -U postgres -f 01_criar_banco.sql
psql -U postgres -d concessionaria_db -f 02_tabelas_e_carga.sql
```

Os scripts foram executados de ponta a ponta no PostgreSQL 16.13. A saída completa,
com cada comando e o resultado das consultas, está em `fontes/saida_execucao.txt`.

## Regerando a documentação

Só é preciso se o grupo quiser mudar o conteúdo pelos scripts em vez de editar o `.docx` direto.

```bash
cd fontes
npm install                    # instala a biblioteca docx
python diagramas.py            # gera ../diagramas/*.svg
node render.js                 # converte os SVGs em PNG (precisa do Playwright)
python coletar_resultados.py   # roda os scripts num PostgreSQL local e grava resultados.json
python paginar.py              # gera o .docx e o .pdf com o sumário paginado (precisa do LibreOffice)
```

| Arquivo em `fontes/` | O que tem |
|---|---|
| `conteudo.js` | Todo o texto do documento: capa, resumo, seções, quadros e referências |
| `montar.js` | A formatação ABNT: margens, fontes, títulos, quadros, códigos e paginação |
| `paginar.py` | Converte para PDF, acha a página de cada título e preenche o sumário e as listas |
| `coletar_resultados.py` | Executa os scripts no PostgreSQL e guarda as saídas mostradas no documento |
| `diagramas.py`, `render.js` | Desenham o MER e o DER |
