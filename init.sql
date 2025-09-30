-- init.sql
-- Este script é executado automaticamente pelo Docker na primeira vez que o container
-- do PostgreSQL é iniciado. Ele cria a estrutura completa do banco de dados
-- para a Parte 2 do projeto e insere alguns dados de exemplo.

-- Limpa tabelas existentes se elas existirem, para garantir um recomeço limpo.
DROP TABLE IF EXISTS ITEM_PEDIDO, PEDIDO, FUNCIONARIO, CLIENTE_TELEFONE, CLIENTE, ENDERECO_CEP, PRODUTO CASCADE;

-- Tabela PRODUTO (Entidade principal da loja)
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

-- Tabela ENDERECO_CEP (Criada para atender a 3ª Forma Normal)
CREATE TABLE ENDERECO_CEP (
    cep VARCHAR(9) NOT NULL,
    logradouro VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    CONSTRAINT pk_endereco_cep PRIMARY KEY (cep)
);

-- Tabela CLIENTE
CREATE TABLE CLIENTE (
    id_cliente SERIAL NOT NULL,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    numero_endereco VARCHAR(20),
    complemento_endereco VARCHAR(100),
    cep VARCHAR(9),
    torce_flamengo BOOLEAN DEFAULT FALSE,
    assiste_one_piece BOOLEAN DEFAULT FALSE,
    natural_de_sousa BOOLEAN DEFAULT FALSE,
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT fk_cliente_endereco_cep FOREIGN KEY (cep) REFERENCES ENDERECO_CEP(cep)
);

-- Tabela CLIENTE_TELEFONE (Criada para atender a 1ª Forma Normal)
CREATE TABLE CLIENTE_TELEFONE (
    id_cliente INTEGER NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    CONSTRAINT pk_cliente_telefone PRIMARY KEY (id_cliente, telefone),
    CONSTRAINT fk_telefone_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE
);

-- Tabela FUNCIONARIO
CREATE TABLE FUNCIONARIO (
    id_funcionario SERIAL NOT NULL,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cargo VARCHAR(50),
    CONSTRAINT pk_funcionario PRIMARY KEY (id_funcionario)
);

-- Tabela PEDIDO
CREATE TABLE PEDIDO (
    id_pedido SERIAL NOT NULL,
    data_pedido TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    forma_pagamento VARCHAR(50) NOT NULL,
    status_pagamento VARCHAR(50) NOT NULL,
    valor_total NUMERIC(10, 2) NOT NULL,
    id_cliente INTEGER NOT NULL,
    id_funcionario INTEGER NOT NULL,
    CONSTRAINT pk_pedido PRIMARY KEY (id_pedido),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    CONSTRAINT fk_pedido_funcionario FOREIGN KEY (id_funcionario) REFERENCES FUNCIONARIO(id_funcionario)
);

-- Tabela ITEM_PEDIDO (Entidade Associativa)
CREATE TABLE ITEM_PEDIDO (
    id_pedido INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario_na_venda NUMERIC(10, 2) NOT NULL,
    CONSTRAINT pk_item_pedido PRIMARY KEY (id_pedido, id_produto),
    CONSTRAINT fk_item_pedido_pedido FOREIGN KEY (id_pedido) REFERENCES PEDIDO(id_pedido) ON DELETE CASCADE,
    CONSTRAINT fk_item_pedido_produto FOREIGN KEY (id_produto) REFERENCES PRODUTO(id_produto)
);


-- Inserção de dados iniciais (seed data)
INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem) VALUES
('Action Figure Luffy Gear 5', 'Estátua do Despertar da Hito Hito no Mi, Modelo: Nika', 199.90, 15, 'Action Figure', false, 'https://storage.geralgeek.com.br/images/venda/Luffy-gear-5-estatua-cerca-de-15cm--6606c5e610c91.jpg'),
('Pôster de Recompensa - Roronoa Zoro', 'Pôster de procurado de Roronoa Zoro após Wano. Berries: 1,111,000,000', 39.90, 50, 'Pôster de Recompensa', true, 'https://i.pinimg.com/236x/27/85/8f/27858f950b04ff0134d387529dd9ff31.jpg'),
('Réplica da Gomu Gomu no Mi', 'Réplica em escala 1:1 da fruta do diabo comida por Monkey D. Luffy.', 89.90, 25, 'Akuma no Mi', false, 'https://geekdama.com.br/wp-content/uploads/2016/03/One-Piece-R%C3%A9plica-Gomu-Gomu-No-Mi-The-Devil-Fruit-2.jpg');

-- Inserindo um funcionário de exemplo (lembre-se que a senha deve ser um hash na aplicação real)
INSERT INTO FUNCIONARIO (nome, email, senha_hash, cargo) VALUES
('Shanks, o Ruivo', 'shanks@yonkou.com', 'pbkdf2:sha256:1000000$BXeZMsLEqLZLDyby$d61607783caa4f2d2de8778bcbd8c0a45dd75efedfed52fe82146ea4021f48bd', 'Capitão');

-- VIEW para simplificar a consulta de vendas por vendedor
CREATE OR REPLACE VIEW V_VENDAS_DETALHADAS AS
SELECT
    f.id_funcionario,
    f.nome AS nome_vendedor,
    p.id_pedido,
    p.data_pedido,
    prod.nome AS nome_produto,
    ip.quantidade,
    ip.preco_unitario_na_venda,
    (ip.quantidade * ip.preco_unitario_na_venda) AS subtotal
FROM PEDIDO p
JOIN FUNCIONARIO f ON p.id_funcionario = f.id_funcionario
JOIN ITEM_PEDIDO ip ON p.id_pedido = ip.id_pedido
JOIN PRODUTO prod ON ip.id_produto = prod.id_produto;

-- Adicione ao final do arquivo init.sql

-- Stored Procedure para criar um pedido completo de forma atômica
CREATE OR REPLACE PROCEDURE criar_pedido_completo(
    p_id_cliente INTEGER,
    p_id_funcionario INTEGER,
    p_forma_pagamento VARCHAR(50),
    p_itens JSON,
    INOUT p_novo_pedido_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    item RECORD;
    produto_info RECORD;
    valor_total_calculado NUMERIC(10, 2) := 0;
    tem_desconto BOOLEAN;
BEGIN
    -- 1. Verifica se o cliente tem direito a desconto
    SELECT (torce_flamengo OR assiste_one_piece OR natural_de_sousa)
    INTO tem_desconto
    FROM CLIENTE WHERE id_cliente = p_id_cliente;

    -- 2. Loop para verificar estoque e calcular o subtotal
    FOR item IN SELECT * FROM json_to_recordset(p_itens) AS x(id_produto INTEGER, quantidade INTEGER)
    LOOP
        -- Trava a linha do produto para evitar condições de corrida
        SELECT preco, quantidade_estoque, nome INTO produto_info FROM PRODUTO WHERE id_produto = item.id_produto FOR UPDATE;

        IF produto_info IS NULL THEN
            RAISE EXCEPTION 'Produto com ID % não encontrado.', item.id_produto;
        END IF;

        IF produto_info.quantidade_estoque < item.quantidade THEN
            RAISE EXCEPTION 'Estoque insuficiente para o produto: %', produto_info.nome;
        END IF;

        valor_total_calculado := valor_total_calculado + (produto_info.preco * item.quantidade);
    END LOOP;

    -- 3. Aplica o desconto, se houver
    IF tem_desconto THEN
        valor_total_calculado := valor_total_calculado * 0.90;
    END IF;

    -- 4. Insere o pedido na tabela principal
    INSERT INTO PEDIDO (id_cliente, id_funcionario, forma_pagamento, status_pagamento, valor_total)
    VALUES (p_id_cliente, p_id_funcionario, p_forma_pagamento, 'Pagamento Aprovado', valor_total_calculado)
    RETURNING id_pedido INTO p_novo_pedido_id;

    -- 5. Loop para inserir os itens do pedido e atualizar o estoque
    FOR item IN SELECT * FROM json_to_recordset(p_itens) AS x(id_produto INTEGER, quantidade INTEGER)
    LOOP
        -- Busca o preço no momento da venda para registrar no item_pedido
        SELECT preco INTO produto_info FROM PRODUTO WHERE id_produto = item.id_produto;

        INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unitario_na_venda)
        VALUES (p_novo_pedido_id, item.id_produto, item.quantidade, produto_info.preco);

        UPDATE PRODUTO SET quantidade_estoque = quantidade_estoque - item.quantidade WHERE id_produto = item.id_produto;
    END LOOP;
END;
$$; 