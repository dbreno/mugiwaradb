import psycopg2
from flask import Flask, jsonify, request # <-- CORREÇÃO AQUI!

# --- Configuração do Banco de Dados ---
# Substitua com suas credenciais do docker-compose.yml
db_config = {
    "host": "localhost",
    "database": "mugiwara_store",
    "user": "luffy",
    "password": "meusonhoeh" 
}

# --- Classe de Acesso a Dados (DAO) para Produto ---
class ProdutoDAO:
    def __init__(self):
        # A DAO usa a configuração definida acima
        self.db_config = db_config

    def _get_connection(self):
        # Método privado para obter uma conexão com o banco
        return psycopg2.connect(**self.db_config)

    def listarTodos(self):
        produtos = []
        try:
            # Pega uma conexão
            conn = self._get_connection()
            cursor = conn.cursor()

            sql_query = "SELECT id_produto, nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari FROM PRODUTO ORDER BY nome;"
            
            # Executa a query
            cursor.execute(sql_query)
            
            # Busca todos os resultados
            resultados = cursor.fetchall()
            
            # Fecha a conexão
            cursor.close()
            conn.close()
            
            # Converte os resultados (tuplas) em uma lista de dicionários para ser mais fácil de usar
            for resultado in resultados:
                produtos.append({
                    'id_produto': resultado[0],
                    'nome': resultado[1],
                    'descricao': resultado[2],
                    'preco': float(resultado[3]), # Converte Decimal para float
                    'quantidade_estoque': resultado[4],
                    'categoria': resultado[5],
                    'fabricado_em_mari': resultado[6]
                })

        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            
        return produtos
      
    def inserir(self, produto):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # SQL com placeholders (%s) para evitar SQL Injection
            sql_query = """
                INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_produto;
            """
            
            # Dados a serem inseridos
            data = (
                produto['nome'],
                produto['descricao'],
                produto['preco'],
                produto['quantidade_estoque'],
                produto['categoria'],
                produto['fabricado_em_mari']
            )

            # Executa a query com os dados
            cursor.execute(sql_query, data)
            
            # Pega o ID do produto recém-criado
            id_produto_novo = cursor.fetchone()[0]
            
            # Confirma a transação
            conn.commit()

            cursor.close()
            conn.close()

            return id_produto_novo

        except Exception as e:
            print(f"Erro ao inserir produto: {e}")
            return None

# --- Aplicação Flask ---
app = Flask(__name__)

# Rota para LER (GET) produtos
@app.route("/api/produtos", methods=['GET'])
def get_produtos():
    dao = ProdutoDAO()
    produtos = dao.listarTodos()
    return jsonify(produtos)

# Rota para CRIAR (POST) produtos
@app.route("/api/produtos", methods=['POST'])
def post_produto():
    dao = ProdutoDAO()
    dados_do_produto = request.get_json()
    
    id_novo = dao.inserir(dados_do_produto)
    
    if id_novo:
        return jsonify({"status": "sucesso", "mensagem": "Produto criado!", "id_produto": id_novo}), 201
    else:
        return jsonify({"status": "erro", "mensagem": "Não foi possível criar o produto."}), 500

# Rota inicial
@app.route("/")
def hello_world():
    return "<p>O servidor da Mugiwara Store está no ar!</p>"

# Permite que o servidor rode
if __name__ == '__main__':
    app.run(debug=True)
