-- init.sql
-- Este script é executado automaticamente pelo Docker na primeira vez que o container
-- do PostgreSQL é iniciado. Ele cria a estrutura inicial do banco de dados e
-- insere alguns dados de exemplo para que a aplicação não comece vazia.

-- Criação da tabela PRODUTO, que é a entidade principal da Parte 1 do projeto.
CREATE TABLE PRODUTO (
    id_produto SERIAL NOT NULL, -- Chave primária autoincremental.
    nome VARCHAR(100) NOT NULL, -- Nome do produto.
    descricao TEXT, -- Descrição detalhada.
    preco NUMERIC(10,2) NOT NULL, -- Preço com 2 casas decimais.
    quantidade_estoque INTEGER NOT NULL, -- Quantidade disponível.
    categoria VARCHAR(50) NOT NULL, -- Categoria do produto.
    fabricado_em_mari BOOLEAN NOT NULL, -- Atributo booleano específico.
    imagem VARCHAR(255), -- Caminho ou URL para a imagem do produto.
    -- Definição das restrições (constraints) da tabela.
    CONSTRAINT pk_produto PRIMARY KEY (id_produto), -- Define id_produto como chave primária.
    CONSTRAINT ck_produto_preco CHECK (preco > 0), -- Garante que o preço seja sempre positivo.
    CONSTRAINT ck_produto_estoque CHECK (quantidade_estoque >= 0) -- Garante que o estoque não seja negativo.
);

-- Inserção de dados iniciais (seed data) para popular a loja.
-- Note que o campo 'imagem' não foi preenchido aqui, ele pode ser adicionado
-- posteriormente através da interface da aplicação.
INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem) VALUES
('Action Figure Luffy Gear 5', 'Estátua do Despertar da Hito Hito no Mi, Modelo: Nika', 199.90, 15, 'Action Figure', false, 'https://storage.geralgeek.com.br/images/venda/Luffy-gear-5-estatua-cerca-de-15cm--6606c5e610c91.jpg'),
('Pôster de Recompensa - Roronoa Zoro', 'Pôster de procurado de Roronoa Zoro após Wano. Berries: 1,111,000,000', 39.90, 50, 'Pôster de Recompensa', true, 'https://i.pinimg.com/236x/27/85/8f/27858f950b04ff0134d387529dd9ff31.jpg'),
('Réplica da Gomu Gomu no Mi', 'Réplica em escala 1:1 da fruta do diabo comida por Monkey D. Luffy.', 89.90, 25, 'Akuma no Mi', false, 'https://geekdama.com.br/wp-content/uploads/2016/03/One-Piece-R%C3%A9plica-Gomu-Gomu-No-Mi-The-Devil-Fruit-2.jpg');