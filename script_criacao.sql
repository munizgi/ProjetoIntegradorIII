-- TABELA PRODUTO ____________________________________________________________________________________________
DROP TABLE IF EXISTS produto CASCADE;
CREATE TABLE produto (
    id_produto        SERIAL PRIMARY KEY NOT NULL,
    descricao_prod    VARCHAR(200)       NOT NULL,
    categoria_prod    VARCHAR(50)        NOT NULL, -- categoria do produto
    procedencia_prod  VARCHAR(50)        NOT NULL, -- de onde veio esse trem
    unidade_base      VARCHAR(10)        NOT NULL, -- pro controle interno de estoque
    u_fator_conversao DECIMAL(10,2)                -- as diversas unidades que podem ser convertidas para venda
                                                    );
-- A unidade de medida da movimentação é apenas operacional,
-- o controle real é feito na unidade base.

-- TABELA LOTE ______________________________________________________________________________________________

DROP TABLE IF EXISTS lote CASCADE;
CREATE TABLE lote (
    id_lote            SERIAL PRIMARY KEY NOT NULL,  --controle interno do banco
    numero_lote        VARCHAR(50)        NOT NULL,  --controle operacional do usuário
    data_validade_lote DATE                          -- rastreabilidade e integridade do lote
                                                    );


-- TABELA TIPO MOVIMENTO _____________________________________________________________________________________

DROP TABLE IF EXISTS tipo_movimento CASCADE;
CREATE TABLE tipo_movimento (
    id_tipo_mov   SERIAL PRIMARY KEY NOT NULL, 
    descricao_mov VARCHAR(50)        NOT NULL --entrada, saída, em processamento
                                                );

-- TABELA TRANSPORTADORA _____________________________________________________________________________________
DROP TABLE IF EXISTS transportadora CASCADE;
CREATE TABLE transportadora (
    id_transp   SERIAL PRIMARY KEY  NOT NULL,
    nome_transp VARCHAR (100)       NOT NULL,
    CNPJ_transp VARCHAR (20) UNIQUE NOT NULL
                                                );

-- TABELA FORNECEDOR __________________________________________________________________________________________

DROP TABLE IF EXISTS fornecedor CASCADE;
CREATE TABLE fornecedor (
    id_fornecedor SERIAL    PRIMARY KEY NOT NULL,
    nome_forn     VARCHAR (150)         NOT NULL,
    CNPJ_forn     VARCHAR (20) UNIQUE   NOT NULL,
    cidade_forn   VARCHAR (50)          NOT NULL,
    estado_forn   VARCHAR (2)           NOT NULL
                                                    );


-- MOVIMENTAÇÃO ESTOQUE (TABELA FILHA) _________________________________________________________________________

DROP TABLE IF EXISTS movimentacao_estoque CASCADE;
CREATE TABLE movimentacao_estoque (
    id_movimento SERIAL PRIMARY KEY NOT NULL, 
    id_prod INT NOT NULL,-- fk
    id_lote INT NOT NULL, --fk
    id_tipo_mov INT NOT NULL, --fk
    id_fornecedor INT, --fk
    id_transp INT, --fk
    data_mov DATE NOT NULL,
    quantidade_prod DECIMAL(12,3) NOT NULL, --qtd de item/produto
    unidade_movimentada VARCHAR(10), -- em que unidade de medida esse prod saiu
    preco_compra DECIMAL(10,2),
    preco_venda DECIMAL(10,2),

    FOREIGN KEY (id_prod) REFERENCES produto(id_prod),
    FOREIGN KEY (id_lote) REFERENCES lote(id_lote),
    FOREIGN KEY (id_tipo_mov) REFERENCES tipo_movimento(id_tipo_mov),
    FOREIGN KEY (id_transp) REFERENCES transportadora(id_transp),
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id_fornecedor)
);

-- ==========================================================================================================================
--                                                     POPULANDO O BD
-- ==========================================================================================================================


