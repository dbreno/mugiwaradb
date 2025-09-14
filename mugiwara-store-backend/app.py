# --- Importações Essenciais ---
import os  # Biblioteca para interagir com o sistema operacional, usada para criar pastas.
import psycopg2  # Driver para conectar o Python ao banco de dados PostgreSQL.
from flask import Flask, jsonify, request, render_template, send_from_directory # Funções e classes do Flask para criar a aplicação web.
from flask_cors import CORS  # Extensão para permitir requisições de outras origens (Cross-Origin Resource Sharing).
from werkzeug.utils import secure_filename  # Função para garantir que nomes de arquivos enviados sejam seguros.

# --- Configuração da Aplicação Flask ---
app = Flask(__name__)  # Inicializa a aplicação Flask.
CORS(app)  # Habilita o CORS para toda a aplicação.

# --- Configuração para Upload de Imagens ---
# Define a pasta onde as imagens dos produtos serão salvas.
UPLOAD_FOLDER = 'static/uploads/produtos'
# Garante que a pasta de upload exista. Se não existir, ela será criada.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Configura a aplicação Flask para usar a pasta definida.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Define as extensões de arquivo que são permitidas para upload.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# --- Configuração do Banco de Dados ---
# Dicionário com as credenciais para conexão com o banco de dados PostgreSQL.
# Estes dados são usados pelo psycopg2 para estabelecer a conexão.
db_config = {
    "host": "localhost",
    "database": "mugiwara_store",
    "user": "luffy",
    "password": "meusonhoeh"
}

# --- Classe de Acesso a Dados (DAO) para Produto ---
# O DAO (Data Access Object) é um padrão de projeto que centraliza toda a lógica
# de interação com o banco de dados para uma entidade específica (neste caso, Produto).
class ProdutoDAO:
    # O construtor da classe.
    def __init__(self):
        self.db_config = db_config

    # Método privado para obter uma nova conexão com o banco de dados.
    # Centralizar isso em um método evita repetição de código.
    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    # Método para listar todos os produtos do banco de dados.
    def listarTodos(self):
        produtos = []
        try:
            # Estabelece a conexão.
            conn = self._get_connection()
            # Cria um cursor, que é o objeto usado para executar comandos SQL.
            cursor = conn.cursor()
            # Query SQL para selecionar todos os campos da tabela PRODUTO, ordenados por nome.
            sql_query = "SELECT id_produto, nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem FROM PRODUTO ORDER BY nome;"
            cursor.execute(sql_query)
            # Pega todos os resultados da consulta.
            resultados = cursor.fetchall()
            # Fecha o cursor e a conexão para liberar os recursos.
            cursor.close()
            conn.close()
            # Transforma cada linha do resultado em um dicionário para facilitar o uso no frontend.
            for resultado in resultados:
                produtos.append({
                    'id_produto': resultado[0],
                    'nome': resultado[1],
                    'descricao': resultado[2],
                    'preco': float(resultado[3]),
                    'quantidade_estoque': resultado[4],
                    'categoria': resultado[5],
                    'fabricado_em_mari': resultado[6],
                    'imagem': resultado[7]
                })
        except Exception as e:
            # Em caso de erro, imprime a exceção no console.
            print(f"Erro ao listar produtos: {e}")
        return produtos

    # Método para pesquisar produtos por nome (busca parcial, case-insensitive).
    def pesquisarPorNome(self, nome):
        produtos = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # O 'ILIKE' é usado para busca case-insensitive no PostgreSQL.
            # Os '%' indicam que o nome pode conter qualquer texto antes ou depois do termo buscado.
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
                    'imagem': resultado[7]
                })
        except Exception as e:
            print(f"Erro ao pesquisar produtos por nome: {e}")
        return produtos

    # Método para inserir um novo produto no banco de dados.
    def inserir(self, produto):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Query SQL para inserir um novo registro.
            # 'RETURNING id_produto' faz com que o banco retorne o ID do produto recém-criado.
            sql_query = """
                INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_produto;
            """
            # Tupla com os dados do produto a serem inseridos.
            data = (
                produto['nome'], produto['descricao'], produto['preco'],
                produto['quantidade_estoque'], produto['categoria'], produto['fabricado_em_mari'],
                produto.get('imagem', '')  # Usa .get() para evitar erro se a chave 'imagem' não existir.
            )
            cursor.execute(sql_query, data)
            # Pega o ID retornado pela query.
            id_produto_novo = cursor.fetchone()[0]
            # Confirma a transação, salvando os dados permanentemente.
            conn.commit()
            cursor.close()
            conn.close()
            return id_produto_novo
        except Exception as e:
            print(f"Erro ao inserir produto: {e}")
            # Se der erro, desfaz a transação.
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            # Garante que a conexão seja fechada, mesmo se ocorrer um erro.
            if 'conn' in locals() and conn is not None:
                conn.close()

    # Método para buscar um único produto pelo seu ID.
    def exibirUm(self, id_produto):
        produto = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT * FROM PRODUTO WHERE id_produto = %s;"
            cursor.execute(sql_query, (id_produto,))
            # Pega apenas o primeiro resultado.
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            if resultado:
                produto = {
                    'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],
                    'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],
                    'categoria': resultado[5], 'fabricado_em_mari': resultado[6],
                    'imagem': resultado[7]
                }
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
        return produto

    # Método para alterar os dados de um produto existente.
    def alterar(self, id_produto, produto_data):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Query SQL para atualizar um registro existente com base no ID.
            sql_query = """
                UPDATE PRODUTO SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s, categoria=%s, fabricado_em_mari=%s, imagem=%s
                WHERE id_produto = %s;
            """
            data = (
                produto_data['nome'], produto_data['descricao'], produto_data['preco'],
                produto_data['quantidade_estoque'], produto_data['categoria'], produto_data['fabricado_em_mari'],
                produto_data.get('imagem', ''),
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

    # Método para remover um produto do banco de dados pelo seu ID.
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

    # Método para gerar um relatório resumido do estoque.
    def gerarRelatorioEstoque(self):
        relatorio = {}
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Query SQL que conta o total de produtos e soma o valor total do estoque.
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

# --- ROTAS DA API ---
# As rotas definem os endpoints da nossa API, ou seja, as URLs que o frontend
# pode chamar para interagir com o backend.

# Rota para listar todos os produtos (GET) ou criar um novo (POST).
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

# Rota para operações em um produto específico (GET, PUT, DELETE).
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

# Rota para buscar produtos por nome.
@app.route("/api/produtos/buscar", methods=['GET'])
def buscar_produto_api():
    nome = request.args.get('nome')
    if not nome:
        return jsonify({"status": "erro", "mensagem": "Parâmetro 'nome' é obrigatório."}), 400
    
    dao = ProdutoDAO()
    produtos = dao.pesquisarPorNome(nome)
    return jsonify(produtos)

# Rota para obter o relatório de estoque.
@app.route("/api/produtos/relatorio", methods=['GET'])
def relatorio_estoque_api():
    dao = ProdutoDAO()
    relatorio = dao.gerarRelatorioEstoque()
    return jsonify(relatorio)

# --- NOVAS ROTAS PARA UPLOAD ---
# Função auxiliar para verificar se a extensão do arquivo é permitida.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para lidar com o upload de imagens.
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Verifica se a requisição contém a parte do arquivo.
    if 'file' not in request.files:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    # Se o usuário não selecionar um arquivo, o navegador envia um arquivo vazio.
    if file.filename == '':
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo selecionado.'}), 400
    # Se o arquivo existir e tiver uma extensão permitida...
    if file and allowed_file(file.filename):
        # Usa secure_filename para evitar nomes de arquivo maliciosos.
        filename = secure_filename(file.filename)
        # Salva o arquivo na pasta de uploads.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Retorna o caminho do arquivo para ser usado no frontend.
        return jsonify({'status': 'sucesso', 'filepath': f'/{filepath}'}), 201
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Tipo de arquivo não permitido.'}), 400

# Rota para servir os arquivos que foram enviados.
# Isso permite que o navegador acesse as imagens pela URL.
@app.route('/static/uploads/produtos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Rota Principal da Aplicação ---
# Rota raiz: Agora serve o `index.html` diretamente.
@app.route("/")
def index():
    return render_template('index.html')

# --- Execução da Aplicação ---
# O bloco `if __name__ == '__main__':` garante que o servidor só rode
# quando o script `app.py` é executado diretamente.
if __name__ == '__main__':
    # `debug=True` ativa o modo de depuração, que reinicia o servidor
    # automaticamente a cada alteração no código.
    app.run(debug=True)