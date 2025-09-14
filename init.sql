CREATE TABLE PRODUTO (
    id_produto SERIAL NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL,
    quantidade_estoque INTEGER NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    fabricado_em_mari BOOLEAN NOT NULL,
    imagem VARCHAR(255),
    CONSTRAINT pk_produto PRIMARY KEY (id_produto),
    CONSTRAINT ck_produto_preco CHECK (preco > 0),
    CONSTRAINT ck_produto_estoque CHECK (quantidade_estoque >= 0)
);

INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari) VALUES
('Action Figure Luffy Gear 5', 'Estátua do Despertar da Hito Hito no Mi, Modelo: Nika', 199.90, 15, 'Action Figure', false),
('Pôster de Recompensa - Roronoa Zoro', 'Pôster de procurado de Roronoa Zoro após Wano. Berries: 1,111,000,000', 39.90, 50, 'Pôster de Recompensa', true),
('Réplica da Gomu Gomu no Mi', 'Réplica em escala 1:1 da fruta do diabo comida por Monkey D. Luffy.', 89.90, 25, 'Akuma no Mi', false);