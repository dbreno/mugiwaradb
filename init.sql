CREATE TABLE PRODUTO (
    id_produto SERIAL NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL,
    quantidade_estoque INTEGER NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    fabricado_em_mari BOOLEAN NOT NULL,
    CONSTRAINT pk_produto PRIMARY KEY (id_produto),
    CONSTRAINT ck_produto_preco CHECK (preco > 0),
    CONSTRAINT ck_produto_estoque CHECK (quantidade_estoque >= 0)
);