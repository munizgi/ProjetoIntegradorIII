-- LIMPA
DROP TABLE IF EXISTS mov_estoque;
DROP TABLE IF EXISTS lotes;
DROP TABLE IF EXISTS transportadora;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS fornecedor;

-- FORNECEDOR
CREATE TABLE fornecedor (
    id SERIAL PRIMARY KEY,
    nome_forn VARCHAR(150),
    cnpj_forn VARCHAR(20),
    cidade_forn VARCHAR(100),
    uf_forn CHAR(2)
);

-- PRODUTO
CREATE TABLE produto (
    id SERIAL PRIMARY KEY,
    descricao_prod VARCHAR(200),
    preco_compra NUMERIC(10,2),
    preco_venda NUMERIC(10,2),
    lucro NUMERIC(10,2),
    qtdep_caixa INTEGER,
    lote_prod VARCHAR(50),
    data_saida DATE,
    data_entrada DATE,
    procedencia_prod VARCHAR(40),
    categoria_prod VARCHAR(100)
);

-- TRANSPORTADORA
CREATE TABLE transportadora (
    id SERIAL PRIMARY KEY,
    nome_transp VARCHAR(150),
    cnpj_transp VARCHAR(20)
);

-- LOTES
CREATE TABLE lotes (
    id SERIAL PRIMARY KEY,
    numero_lote VARCHAR(50),
    data_validade DATE
);

-- MOVIMENTAÇÃO
CREATE TABLE mov_estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER,
    fornecedor_id INTEGER,
    transportadora_id INTEGER,
    lote_id INTEGER,
    tipo_mov VARCHAR(20),
    data DATE,
    qtde_prod NUMERIC(10,2),
    unidade_medida VARCHAR(20),

    FOREIGN KEY (produto_id) REFERENCES produto(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedor(id),
    FOREIGN KEY (transportadora_id) REFERENCES transportadora(id),
    FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

SELECT * FROM mov_estoque;

SELECT * FROM fornecedor;

SELECT * FROM produto;

SELECT * FROM transportadora;

SELECT * FROM lotes;