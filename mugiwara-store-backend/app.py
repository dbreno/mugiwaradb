# --- Importações Essenciais ---
# Importa bibliotecas necessárias para o funcionamento da aplicação
import os  # Para manipulação de arquivos e variáveis de ambiente
import psycopg2  # Para conexão com o banco de dados PostgreSQL
from flask import Flask, jsonify, request, render_template, send_from_directory  # Framework Flask para criar a API
from flask_cors import CORS  # Para permitir requisições de diferentes origens (CORS)
from werkzeug.utils import secure_filename  # Para manipulação segura de nomes de arquivos
from werkzeug.security import generate_password_hash, check_password_hash  # Para segurança de senhas
import jwt  # Para geração e validação de tokens JWT (autenticação)
from datetime import datetime, timedelta  # Para manipulação de datas e tempos
from functools import wraps  # Para criar decorators (funções que modificam outras funções)

# --- Configuração da Aplicação Flask ---
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "o_tesouro_one_piece_existe")

# --- Configuração para Upload de Imagens ---
UPLOAD_FOLDER = 'static/uploads/produtos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# --- Configuração do Banco de Dados ---
db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("POSTGRES_DB", "mugiwara_store"),
    "user": os.getenv("POSTGRES_USER", "luffy"),
    "password": os.getenv("POSTGRES_PASSWORD", "meusonhoeh")
}

# --- DECORATOR DE AUTENTICAÇÃO ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token está faltando!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token é inválido!'}), 401
        return f(data, *args, **kwargs)
    return decorated

# --- CLASSES DE ACESSO A DADOS (DAOs) ---
class BaseDAO:
    def __init__(self):
        self.db_config = db_config
    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

class ProdutoDAO(BaseDAO):
    def listarTodos(self):
        produtos = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT id_produto, nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem FROM PRODUTO ORDER BY nome;"
            cursor.execute(sql_query)
            resultados = cursor.fetchall()
            for resultado in resultados:
                produtos.append({'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],'categoria': resultado[5], 'fabricado_em_mari': resultado[6], 'imagem': resultado[7]})
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        return produtos

    def pesquisarPorNome(self, nome):
        produtos = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT * FROM PRODUTO WHERE nome ILIKE %s;"
            cursor.execute(sql_query, (f'%{nome}%',))
            resultados = cursor.fetchall()
            for resultado in resultados:
                produtos.append({'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],'categoria': resultado[5], 'fabricado_em_mari': resultado[6], 'imagem': resultado[7]})
        except Exception as e:
            print(f"Erro ao pesquisar produtos por nome: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        return produtos

    def inserir(self, produto):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "INSERT INTO PRODUTO (nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_produto;"
            data = (produto['nome'], produto['descricao'], produto['preco'], produto['quantidade_estoque'], produto['categoria'], produto['fabricado_em_mari'], produto.get('imagem', ''))
            cursor.execute(sql_query, data)
            id_produto_novo = cursor.fetchone()[0]
            conn.commit()
            return id_produto_novo
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao inserir produto: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    def exibirUm(self, id_produto):
        produto = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT * FROM PRODUTO WHERE id_produto = %s;"
            cursor.execute(sql_query, (id_produto,))
            resultado = cursor.fetchone()
            if resultado:
                produto = {'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2], 'preco': float(resultado[3]), 'quantidade_estoque': resultado[4], 'categoria': resultado[5], 'fabricado_em_mari': resultado[6], 'imagem': resultado[7]}
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        return produto

    def alterar(self, id_produto, produto_data):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "UPDATE PRODUTO SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s, categoria=%s, fabricado_em_mari=%s, imagem=%s WHERE id_produto = %s;"
            data = (produto_data['nome'], produto_data['descricao'], produto_data['preco'], produto_data['quantidade_estoque'], produto_data['categoria'], produto_data['fabricado_em_mari'], produto_data.get('imagem', ''), id_produto)
            cursor.execute(sql_query, data)
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao alterar produto: {e}")
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()

    def remover(self, id_produto):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "DELETE FROM PRODUTO WHERE id_produto = %s;"
            cursor.execute(sql_query, (id_produto,))
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao remover produto: {e}")
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()

    def gerarRelatorioEstoque(self):
        relatorio = {}
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT COUNT(*), SUM(preco * quantidade_estoque) FROM PRODUTO;"
            cursor.execute(sql_query)
            resultado = cursor.fetchone()
            if resultado:
                relatorio = {'total_de_produtos_distintos': resultado[0], 'valor_total_do_estoque': float(resultado[1]) if resultado[1] is not None else 0.0}
        except Exception as e:
            print(f"Erro ao gerar relatório de estoque: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        return relatorio

class ClienteDAO(BaseDAO):
    def registrar(self, cliente_data):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            conn.autocommit = False

            cep_data = cliente_data.get('endereco', {})
            # --- CORREÇÃO AQUI: Garante que o CEP é None se for uma string vazia ---
            cep_valor = cep_data.get('cep') if cep_data and cep_data.get('cep') else None

            if cep_valor:
                sql_cep = "INSERT INTO ENDERECO_CEP (cep, logradouro, bairro, cidade, estado) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (cep) DO NOTHING;"
                cursor.execute(sql_cep, (cep_valor, cep_data.get('logradouro', ''), cep_data.get('bairro', ''), cep_data.get('cidade', ''), cep_data.get('estado', '')))

            senha_hash = generate_password_hash(cliente_data['senha']).decode('utf-8')
            sql_cliente = "INSERT INTO CLIENTE (nome, email, senha_hash, numero_endereco, complemento_endereco, cep, torce_flamengo, assiste_one_piece, natural_de_sousa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_cliente"
            cursor.execute(sql_cliente, (
                cliente_data['nome'], cliente_data['email'], senha_hash,
                cep_data.get('numero_endereco'), cep_data.get('complemento_endereco'), cep_valor,
                cliente_data.get('torce_flamengo', False), cliente_data.get('assiste_one_piece', False), cliente_data.get('natural_de_sousa', False)
            ))
            id_novo = cursor.fetchone()[0]

            telefone = cliente_data.get('telefone')
            if telefone:
                sql_telefone = "INSERT INTO CLIENTE_TELEFONE (id_cliente, telefone) VALUES (%s, %s)"
                cursor.execute(sql_telefone, (id_novo, telefone))

            conn.commit()
            return id_novo
        except psycopg2.IntegrityError as e:
            if conn: conn.rollback()
            if 'cliente_email_key' in str(e):
                return "Email já cadastrado."
            print(f"Erro de integridade de dados no registro: {e}")
            return "Erro de integridade de dados. Verifique se o CEP é válido."
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao registrar cliente: {e}")
            return None
        finally:
            if conn:
                conn.autocommit = True
                cursor.close()
                conn.close()

    def buscar_por_email(self, email):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = "SELECT id_cliente, nome, email, senha_hash FROM CLIENTE WHERE email = %s"
            cursor.execute(sql, (email,))
            cliente = cursor.fetchone()
            if cliente:
                return {'id': cliente[0], 'nome': cliente[1], 'email': cliente[2], 'senha_hash': cliente[3], 'tipo': 'cliente'}
            return None
        except Exception as e:
            print(f"Erro ao buscar cliente por email: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

class FuncionarioDAO(BaseDAO):
    def buscar_por_email(self, email):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = "SELECT id_funcionario, nome, email, senha_hash, cargo FROM FUNCIONARIO WHERE email = %s"
            cursor.execute(sql, (email,))
            func = cursor.fetchone()
            if func:
                return {'id': func[0], 'nome': func[1], 'email': func[2], 'senha_hash': func[3], 'cargo': func[4], 'tipo': 'funcionario'}
            return None
        except Exception as e:
            print(f"Erro ao buscar funcionário por email: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

class PedidoDAO(BaseDAO):
    def criar_pedido(self, id_cliente, id_funcionario, carrinho):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            conn.autocommit = False

            valor_total_calculado = 0
            for item in carrinho['itens']:
                sql_verifica_estoque = "SELECT nome, preco, quantidade_estoque FROM PRODUTO WHERE id_produto = %s FOR UPDATE"
                cursor.execute(sql_verifica_estoque, (item['id_produto'],))
                produto = cursor.fetchone()
                if produto is None: raise Exception(f"Produto com ID {item['id_produto']} não encontrado.")
                if produto[2] < item['quantidade']: raise Exception(f"Estoque insuficiente para o produto '{produto[0]}'.")
                valor_total_calculado += produto[1] * item['quantidade']

            sql_cria_pedido = "INSERT INTO PEDIDO (id_cliente, id_funcionario, forma_pagamento, status_pagamento, valor_total) VALUES (%s, %s, %s, %s, %s) RETURNING id_pedido"
            cursor.execute(sql_cria_pedido, (id_cliente, id_funcionario, carrinho['forma_pagamento'], 'Pagamento Aprovado', valor_total_calculado))
            novo_pedido_id = cursor.fetchone()[0]

            for item in carrinho['itens']:
                cursor.execute("SELECT preco FROM PRODUTO WHERE id_produto = %s", (item['id_produto'],))
                preco_unitario = cursor.fetchone()[0]
                sql_insere_item = "INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unitario_na_venda) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_insere_item, (novo_pedido_id, item['id_produto'], item['quantidade'], preco_unitario))
                sql_atualiza_estoque = "UPDATE PRODUTO SET quantidade_estoque = quantidade_estoque - %s WHERE id_produto = %s"
                cursor.execute(sql_atualiza_estoque, (item['quantidade'], item['id_produto']))

            conn.commit()
            return {"status": "sucesso", "id_pedido": novo_pedido_id}
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao criar pedido: {e}")
            return {"status": "erro", "mensagem": str(e)}
        finally:
            if conn:
                conn.autocommit = True
                cursor.close()
                conn.close()

# --- ROTAS DA APLICAÇÃO ---
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/api/registrar', methods=['POST'])
def registrar_cliente():
    dados = request.get_json()
    if not dados or not dados.get('email') or not dados.get('senha') or not dados.get('nome'):
        return jsonify({'message': 'Dados essenciais (nome, email, senha) são obrigatórios.'}), 400
    dao = ClienteDAO()
    resultado = dao.registrar(dados)
    if isinstance(resultado, int):
        return jsonify({'message': 'Cliente registrado com sucesso!', 'id_cliente': resultado}), 201
    elif isinstance(resultado, str):
        return jsonify({'message': resultado}), 409
    else:
        return jsonify({'message': 'Erro no servidor ao registrar.'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('senha'):
        return jsonify({'message': 'Não foi possível verificar'}), 401
    user_dao = FuncionarioDAO()
    user = user_dao.buscar_por_email(auth['email'])
    if not user:
        user_dao = ClienteDAO()
        user = user_dao.buscar_por_email(auth['email'])
    if not user:
        return jsonify({'message': 'Email não encontrado!'}), 401
    if check_password_hash(user['senha_hash'], auth['senha']):
        token = jwt.encode({'id': user['id'], 'tipo': user['tipo'], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Senha incorreta!'}), 401

@app.route('/api/pedidos', methods=['POST'])
@token_required
def criar_pedido_api(current_user):
    if current_user['tipo'] != 'cliente':
        return jsonify({'message': 'Acesso negado: apenas clientes podem fazer compras.'}), 403
    dados_carrinho = request.get_json()
    if not dados_carrinho or 'itens' not in dados_carrinho or not dados_carrinho['itens']:
        return jsonify({'message': 'Carrinho vazio ou dados inválidos.'}), 400
    id_cliente = current_user['id']
    id_funcionario = 1
    dao = PedidoDAO()
    resultado = dao.criar_pedido(id_cliente, id_funcionario, dados_carrinho)
    if resultado['status'] == 'sucesso':
        return jsonify(resultado), 201
    else:
        return jsonify(resultado), 400

@app.route("/api/produtos", methods=['GET', 'POST'])
def produtos_api():
    dao = ProdutoDAO()
    if request.method == 'GET':
        return jsonify(dao.listarTodos())
    if request.method == 'POST':
        @token_required
        def criar_produto(current_user):
            if current_user['tipo'] != 'funcionario':
                return jsonify({'message': 'Acesso negado!'}), 403
            dados_do_produto = request.get_json()
            id_novo = dao.inserir(dados_do_produto)
            if id_novo:
                return jsonify({"status": "sucesso", "mensagem": "Produto criado!", "id_produto": id_novo}), 201
            else:
                return jsonify({"status": "erro", "mensagem": "Não foi possível criar o produto."}), 500
        return criar_produto()

@app.route("/api/produtos/<int:id_produto>", methods=['GET', 'PUT', 'DELETE'])
def produto_especifico_api(id_produto):
    dao = ProdutoDAO()
    if request.method == 'GET':
        produto = dao.exibirUm(id_produto)
        if produto:
            return jsonify(produto)
        else:
            return jsonify({"status": "erro", "mensagem": "Produto não encontrado."}), 404
    @token_required
    def operacao_protegida(current_user):
        if current_user['tipo'] != 'funcionario':
            return jsonify({'message': 'Acesso negado!'}), 403
        if request.method == 'PUT':
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
    return operacao_protegida()

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if current_user['tipo'] != 'funcionario':
        return jsonify({'message': 'Acesso negado!'}), 403
    if 'file' not in request.files:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo selecionado.'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'status': 'sucesso', 'filepath': f'/{filepath}'}), 201
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Tipo de arquivo não permitido.'}), 400

@app.route('/static/uploads/produtos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)