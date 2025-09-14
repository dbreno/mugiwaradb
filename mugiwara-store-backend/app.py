import psycopg2
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# --- Configuração do Banco de Dados ---
db_config = {
    "host": "localhost",
    "database": "mugiwara_store",
    "user": "luffy",
    "password": "meusonhoeh"
}

# --- Classe de Acesso a Dados (DAO) para Produto ---
class ProdutoDAO:
    def __init__(self):
        self.db_config = db_config

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def listarTodos(self):
        produtos = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT id_produto, nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem FROM PRODUTO ORDER BY nome;"
            cursor.execute(sql_query)
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            for resultado in resultados:
                produtos.append({
                    'id_produto': resultado[0],
                    'nome': resultado[1],
                    'descricao': resultado[2],
                    'preco': float(resultado[3]),
                    'quantidade_estoque': resultado[4],
                    'categoria': resultado[5],
                    'fabricado_em_mari': resultado[6],
                    'imagem': resultado[7]  # Novo campo
                })
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
        return produtos

    def pesquisarPorNome(self, nome):
        produtos = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT * FROM PRODUTO WHERE nome ILIKE %s;"
            cursor.execute(sql_query, (f'%{nome}%',))
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            for resultado in resultados:
                produtos.append({
                    'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],
                    'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],
                    'categoria': resultado[5], 'fabricado_em_mari': resultado[6],
                    'imagem': resultado[7]  # Novo campo
                })
        except Exception as e:
            print(f"Erro ao pesquisar produtos por nome: {e}")
        return produtos

    def inserir(self, produto):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = """
                INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_produto;
            """
            data = (
                produto['nome'], produto['descricao'], produto['preco'],
                produto['quantidade_estoque'], produto['categoria'], produto['fabricado_em_mari'],
                produto.get('imagem', '')  # Novo campo, default vazio
            )
            cursor.execute(sql_query, data)
            id_produto_novo = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return id_produto_novo
        except Exception as e:
            print(f"Erro ao inserir produto: {e}")
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    def exibirUm(self, id_produto):
        produto = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT * FROM PRODUTO WHERE id_produto = %s;"
            cursor.execute(sql_query, (id_produto,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            if resultado:
                produto = {
                    'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],
                    'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],
                    'categoria': resultado[5], 'fabricado_em_mari': resultado[6],
                    'imagem': resultado[7]  # Novo campo
                }
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
        return produto

    def alterar(self, id_produto, produto_data):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = """
                UPDATE PRODUTO SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s, categoria=%s, fabricado_em_mari=%s, imagem=%s
                WHERE id_produto = %s;
            """
            data = (
                produto_data['nome'], produto_data['descricao'], produto_data['preco'],
                produto_data['quantidade_estoque'], produto_data['categoria'], produto_data['fabricado_em_mari'],
                produto_data.get('imagem', ''),  # Novo campo
                id_produto
            )
            cursor.execute(sql_query, data)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao alterar produto: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    def remover(self, id_produto):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "DELETE FROM PRODUTO WHERE id_produto = %s;"
            cursor.execute(sql_query, (id_produto,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao remover produto: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    def gerarRelatorioEstoque(self):
        relatorio = {}
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT COUNT(*), SUM(preco * quantidade_estoque) FROM PRODUTO;"
            cursor.execute(sql_query)
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            if resultado:
                relatorio = {
                    'total_de_produtos_distintos': resultado[0],
                    'valor_total_do_estoque': float(resultado[1]) if resultado[1] is not None else 0.0
                }
        except Exception as e:
            print(f"Erro ao gerar relatório de estoque: {e}")
        return relatorio

# --- Aplicação Flask ---
app = Flask(__name__)
CORS(app)

# --- ROTAS DA API ---
@app.route("/api/produtos", methods=['GET', 'POST'])
def produtos_api():
    dao = ProdutoDAO()
    if request.method == 'GET':
        return jsonify(dao.listarTodos())
    elif request.method == 'POST':
        dados_do_produto = request.get_json()
        id_novo = dao.inserir(dados_do_produto)
        if id_novo:
            return jsonify({"status": "sucesso", "mensagem": "Produto criado!", "id_produto": id_novo}), 201
        else:
            return jsonify({"status": "erro", "mensagem": "Não foi possível criar o produto."}), 500

@app.route("/api/produtos/<int:id_produto>", methods=['GET', 'PUT', 'DELETE'])
def produto_especifico_api(id_produto):
    dao = ProdutoDAO()
    
    if request.method == 'GET':
        produto = dao.exibirUm(id_produto)
        if produto:
            return jsonify(produto)
        else:
            return jsonify({"status": "erro", "mensagem": "Produto não encontrado."}), 404

    elif request.method == 'PUT':
        dados_do_produto = request.get_json()
        if dao.alterar(id_produto, dados_do_produto):
            return jsonify({"status": "sucesso", "mensagem": "Produto alterado!"})
        else:
            return jsonify({"status": "erro", "mensagem": "Não foi possível alterar o produto."}), 500

    elif request.method == 'DELETE':
        if dao.remover(id_produto):
            return jsonify({"status": "sucesso", "mensagem": "Produto removido!"})
        else:
            return jsonify({"status": "erro", "mensagem": "Não foi possível remover o produto."}), 500

@app.route("/api/produtos/buscar", methods=['GET'])
def buscar_produto_api():
    nome = request.args.get('nome')
    if not nome:
        return jsonify({"status": "erro", "mensagem": "Parâmetro 'nome' é obrigatório."}), 400
    
    dao = ProdutoDAO()
    produtos = dao.pesquisarPorNome(nome)
    return jsonify(produtos)

@app.route("/api/produtos/relatorio", methods=['GET'])
def relatorio_estoque_api():
    dao = ProdutoDAO()
    relatorio = dao.gerarRelatorioEstoque()
    return jsonify(relatorio)

# Rota raiz: Agora serve o index.html diretamente
@app.route("/")
def index():
    return render_template('index.html')  # Renderiza o template index.html

# Permite que o servidor rode
if __name__ == '__main__':
    app.run(debug=True)