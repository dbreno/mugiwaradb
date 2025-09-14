# Mugiwara Store DB 🏴‍☠️

![One Piece Banner](https://i.ibb.co/Kz7gzM6B/one-piece-character-5120x2880-15328.jpg)

## Sobre o Projeto

**Mugiwara Store** é um sistema de e-commerce web totalmente funcional, desenvolvido como parte do projeto da disciplina de Banco de Dados I. A aplicação consiste em um CRUD (Create, Read, Update, Delete) completo para o gerenciamento de produtos de uma loja com a temática do universo de One Piece.

Este repositório contém a **Parte 1** do projeto, que foca no núcleo de gerenciamento de produtos e estoque, com uma API RESTful no backend e uma interface reativa e estilizada no frontend. Toda a aplicação é orquestrada com Docker, garantindo um ambiente de desenvolvimento consistente e de fácil configuração.

## Funcionalidades Implementadas

A aplicação web implementa todas as funcionalidades CRUD exigidas e vai além, oferecendo uma experiência de usuário rica e moderna.

* **Gerenciamento de Produtos (CRUD):**
    * **Criação:** Adicionar novos produtos (tesouros) ao catálogo através de um formulário modal.
    * **Leitura:** Listagem de todos os produtos em cards visuais na página principal.
    * **Atualização:** Edição de informações de produtos existentes no mesmo modal.
    * **Exclusão:** Remover produtos do catálogo com uma caixa de confirmação.
* **Busca e Filtros Avançados:**
    * Busca por nome do produto.
    * Filtro dinâmico por categoria.
    * Filtro por faixa de preço (mínimo e máximo).
    * Ordenação por nome (A-Z, Z-A) e preço (maior, menor).
* **Upload de Imagens:**
    * Suporte para adicionar imagens via **URL externa** ou fazendo **upload de um arquivo local**.
    * Pré-visualização da imagem no formulário antes de salvar.
* **Relatórios:**
    * Geração de um relatório de estoque que exibe a quantidade total de produtos distintos e o valor total do inventário.

## Tecnologias Utilizadas

O projeto foi construído com uma stack de tecnologias modernas e eficientes:

* **Backend:**
    * **Python 3.9**
    * **Flask:** Micro-framework para a criação da API RESTful.
    * **Psycopg2:** Driver para a conexão entre Python e PostgreSQL.
* **Frontend:**
    * **HTML5** e **CSS3**.
    * **Vue.js 3:** Framework JavaScript para criar a interface reativa.
    * **Tailwind CSS:** Framework CSS para estilização rápida e customizada.
* **Banco de Dados:**
    * **PostgreSQL 16:** Sistema de Gerenciamento de Banco de Dados Relacional.
* **Ambiente:**
    * **Docker & Docker Compose:** Para containerização e orquestração dos serviços, garantindo um ambiente de desenvolvimento consistente e isolado.

## Como Executar o Projeto

Graças ao Docker, colocar a aplicação para rodar é um processo simples e rápido.

### Pré-requisitos

* **Docker:** [Link para instalação](https://docs.docker.com/get-docker/)
* **Docker Compose:** (geralmente já vem com o Docker Desktop)

### Passos para Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/dbreno/mugiwaradb.git](https://github.com/dbreno/mugiwaradb.git)
    cd mugiwaradb
    ```

2.  **Construa e inicie os contêineres:**
    Execute o seguinte comando na raiz do projeto:
    ```bash
    docker compose up --build
    ```
    * O comando irá construir a imagem do backend, baixar a imagem do PostgreSQL e iniciar ambos os serviços.
    * O banco de dados será automaticamente criado e populado com os dados do arquivo `init.sql` na primeira vez que for executado.

3.  **Acesse a aplicação:**
    Abra seu navegador e acesse:
    [**http://localhost:5000**](http://localhost:5000)

4.  **Para parar a aplicação:**
    Pressione `CTRL + C` no terminal onde os contêineres estão rodando ou, de outro terminal, execute:
    ```bash
    docker compose down
    ```

## Acesso ao Banco de Dados (DBeaver/Outros)

Enquanto os contêineres estiverem rodando, você pode se conectar ao banco de dados PostgreSQL usando sua ferramenta de preferência (como o DBeaver) com as seguintes credenciais:

* **Host:** `localhost`
* **Porta:** `5432`
* **Banco de Dados:** `mugiwara_store`
* **Usuário:** `luffy`
* **Senha:** `meusonhoeh`