# --- Importações Essenciais ---
# Importa bibliotecas necessárias para o funcionamento da aplicação
import os  # Para manipulação de arquivos e variáveis de ambiente
import psycopg2  # Para conexão com o banco de dados PostgreSQL
import json 
from decimal import Decimal  # Para manipulação precisa de valores monetários
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
    
    def listar_estoque_baixo(self):
        produtos = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql_query = "SELECT id_produto, nome, descricao, preco, quantidade_estoque, categoria, fabricado_em_mari, imagem FROM PRODUTO WHERE quantidade_estoque < 5 ORDER BY quantidade_estoque;"
            cursor.execute(sql_query)
            resultados = cursor.fetchall()
            for resultado in resultados:
                produtos.append({'id_produto': resultado[0], 'nome': resultado[1], 'descricao': resultado[2],'preco': float(resultado[3]), 'quantidade_estoque': resultado[4],'categoria': resultado[5], 'fabricado_em_mari': resultado[6], 'imagem': resultado[7]})
        except Exception as e:
            print(f"Erro ao listar produtos com estoque baixo: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        return produtos

class ClienteDAO(BaseDAO):
    def registrar(self, cliente_data):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            conn.autocommit = False

            cep_data = cliente_data.get('endereco', {})
            cep_valor = cep_data.get('cep') if cep_data and cep_data.get('cep') else None

            if cep_valor:
                sql_cep = "INSERT INTO ENDERECO_CEP (cep, logradouro, bairro, cidade, estado) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (cep) DO NOTHING;"
                cursor.execute(sql_cep, (cep_valor, cep_data.get('logradouro', ''), cep_data.get('bairro', ''), cep_data.get('cidade', ''), cep_data.get('estado', '')))

            senha_hash = generate_password_hash(cliente_data['senha'])
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
            # Query correta na tabela CLIENTE, buscando as flags de desconto
            sql = "SELECT id_cliente, nome, email, senha_hash, torce_flamengo, assiste_one_piece, natural_de_sousa FROM CLIENTE WHERE email = %s"
            cursor.execute(sql, (email,))
            cliente = cursor.fetchone()
            if cliente:
                # Retorno correto para o tipo 'cliente' com as flags
                return {
                    'id': cliente[0],
                    'nome': cliente[1],
                    'email': cliente[2],
                    'senha_hash': cliente[3],
                    'tipo': 'cliente',
                    'flags_desconto': (cliente[4], cliente[5], cliente[6])
                }
            return None
        except Exception as e:
            print(f"Erro ao buscar cliente por email: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def buscar_por_id(self, id_cliente):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = """
                SELECT c.nome, c.email, t.telefone, ec.cep, ec.logradouro,
                        c.numero_endereco, c.complemento_endereco, ec.bairro,
                        ec.cidade, ec.estado
                FROM CLIENTE c
                LEFT JOIN CLIENTE_TELEFONE t ON c.id_cliente = t.id_cliente
                LEFT JOIN ENDERECO_CEP ec ON c.cep = ec.cep
                WHERE c.id_cliente = %s LIMIT 1
            """
            cursor.execute(sql, (id_cliente,))
            cliente = cursor.fetchone()
            if cliente:
                return {
                    'nome': cliente[0], 'email': cliente[1], 'telefone': cliente[2],
                    'endereco': {
                        'cep': cliente[3], 'logradouro': cliente[4],
                        'numero': cliente[5], 'complemento': cliente[6],
                        'bairro': cliente[7], 'cidade': cliente[8], 'estado': cliente[9]
                    }
                }
            return None
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
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
            # Query correta na tabela FUNCIONARIO
            sql = "SELECT id_funcionario, nome, email, senha_hash, cargo FROM FUNCIONARIO WHERE email = %s"
            cursor.execute(sql, (email,))
            func = cursor.fetchone()
            if func:
                # Retorno correto para o tipo 'funcionario'
                return {
                    'id': func[0],
                    'nome': func[1],
                    'email': func[2],
                    'senha_hash': func[3],
                    'cargo': func[4],
                    'tipo': 'funcionario'
                }
            return None
        except Exception as e:
            print(f"Erro ao buscar funcionário por email: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    def listar_todos(self):
        vendedores = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Busca o ID e o nome de todos os funcionários para a lista de seleção
            sql = "SELECT id_funcionario, nome FROM FUNCIONARIO ORDER BY nome"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            for r in resultados:
                vendedores.append({'id': r[0], 'nome': r[1]})
            return vendedores
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    def registrar(self, func_data):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            senha_hash = generate_password_hash(func_data['senha'])
            
            sql = "INSERT INTO FUNCIONARIO (nome, email, senha_hash, cargo) VALUES (%s, %s, %s, %s) RETURNING id_funcionario"
            cursor.execute(sql, (
                func_data['nome'],
                func_data['email'],
                senha_hash,
                func_data.get('cargo', 'Vendedor')
            ))
            id_novo = cursor.fetchone()[0]
            conn.commit()
            return id_novo
        except psycopg2.IntegrityError:
            if conn: conn.rollback()
            return "Email já cadastrado."
        except Exception as e:
            if conn: conn.rollback()
            print(f"Erro ao registrar funcionário: {e}")
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
            
            # Converte a lista de itens do carrinho para uma string no formato JSON,
            # que é o que a nossa Stored Procedure espera.
            itens_json = json.dumps(carrinho['itens'])

            # O último parâmetro (p_novo_pedido_id) é INOUT, então passamos um valor inicial (0).
            # A procedure irá modificá-lo e nos retornar o ID do novo pedido.
            # Infelizmente, o psycopg2 não lida bem com parâmetros INOUT em CALL.
            # Uma abordagem mais robusta seria usar uma FUNCTION, mas para manter a exigência
            # de uma PROCEDURE, vamos fazer uma pequena adaptação.
            
            # Vamos transformar a procedure em uma FUNCTION temporariamente para facilitar a chamada
            # A lógica é a mesma, mas a forma de chamar do Python fica mais limpa.
            
            # (A melhor abordagem é modificar a Stored Procedure para ser uma FUNCTION no SQL)
            # Por simplicidade aqui, vamos chamar a procedure e depois buscar o último ID.
            # Esta não é a forma ideal em produção, mas cumpre o requisito.
            
            # Chamada à Stored Procedure. Passamos 0 como placeholder para o parâmetro INOUT.
            sql_call = "CALL criar_pedido_completo(%s, %s, %s, %s, %s);"
            # Para pegar o ID de volta, a forma mais segura é buscar o último pedido do cliente.
            
            cursor.execute("BEGIN;") # Inicia a transação
            cursor.execute(sql_call, (id_cliente, id_funcionario, carrinho['forma_pagamento'], itens_json, 0))
            
            # Busca o ID do último pedido inserido por este cliente nesta sessão
            cursor.execute("SELECT id_pedido FROM PEDIDO WHERE id_cliente = %s ORDER BY data_pedido DESC LIMIT 1;", (id_cliente,))
            novo_pedido_id = cursor.fetchone()[0]
            
            conn.commit() # Confirma a transação
            
            return {"status": "sucesso", "id_pedido": novo_pedido_id}
        except Exception as e:
            if conn: conn.rollback() # Desfaz a transação em caso de erro
            
            # Extrai a mensagem de erro vinda do banco (ex: "Estoque insuficiente...")
            mensagem_erro = str(e).split('CONTEXT:')[0].strip()
            print(f"Erro ao chamar procedure de pedido: {mensagem_erro}")
            return {"status": "erro", "mensagem": mensagem_erro}
        finally:
            if conn:
                cursor.close()
                conn.close()

    def listar_por_cliente(self, id_cliente):
        pedidos = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = """
                SELECT id_pedido, data_pedido, valor_total, forma_pagamento, status_pagamento
                FROM PEDIDO
                WHERE id_cliente = %s
                ORDER BY data_pedido DESC
            """
            cursor.execute(sql, (id_cliente,))
            resultados = cursor.fetchall()
            for r in resultados:
                pedidos.append({
                    'id_pedido': r[0],
                    'data': r[1].strftime('%d/%m/%Y %H:%M'),
                    'total': float(r[2]),
                    'pagamento': r[3],
                    'status': r[4]
                })
            return pedidos
        except Exception as e:
            print(f"Erro ao listar pedidos do cliente: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

class RelatorioDAO(BaseDAO):
    def gerar_relatorio_vendas_mensal(self):
        relatorio = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Esta query usa a nossa VIEW e agrupa os resultados por vendedor,
            # somando o total de vendas (subtotal) e contando o número de vendas.
            # Ela filtra os resultados para o mês e ano atuais.
            sql = """
                SELECT 
                    nome_vendedor, 
                    COUNT(DISTINCT id_pedido) as total_pedidos, 
                    SUM(subtotal) as valor_total_vendido
                FROM V_VENDAS_DETALHADAS
                WHERE EXTRACT(MONTH FROM data_pedido) = EXTRACT(MONTH FROM CURRENT_DATE)
                  AND EXTRACT(YEAR FROM data_pedido) = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY nome_vendedor
                ORDER BY valor_total_vendido DESC;
            """
            cursor.execute(sql)
            resultados = cursor.fetchall()
            for r in resultados:
                relatorio.append({
                    'vendedor': r[0],
                    'pedidos_realizados': r[1],
                    'total_vendido': float(r[2])
                })
            return relatorio
        except Exception as e:
            print(f"Erro ao gerar relatório de vendas mensal: {e}")
            return None
        finally:
            if conn:
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
    
    # Tenta logar como funcionário primeiro
    user_dao = FuncionarioDAO()
    user = user_dao.buscar_por_email(auth['email'])
    
    # Se não for funcionário, tenta como cliente
    if not user:
        user_dao = ClienteDAO()
        user = user_dao.buscar_por_email(auth['email'])

    if not user:
        return jsonify({'message': 'Email não encontrado!'}), 401

    if check_password_hash(user['senha_hash'], auth['senha']):
        # --- INÍCIO DA ALTERAÇÃO ---
        
        # Cria o payload base do token
        payload = {
            'id': user['id'],
            'tipo': user['tipo'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        # Se o usuário for um cliente, verifica e adiciona a flag de desconto
        if user['tipo'] == 'cliente':
            tem_desconto = any(user['flags_desconto'])
            payload['tem_desconto'] = tem_desconto

        # --- FIM DA ALTERAÇÃO ---
        
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
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

@app.route('/api/cliente/perfil', methods=['GET'])
@token_required
def get_cliente_perfil(current_user):
    if current_user['tipo'] != 'cliente':
        return jsonify({'message': 'Acesso negado'}), 403

    dao = ClienteDAO()
    perfil = dao.buscar_por_id(current_user['id'])
    if perfil:
        return jsonify(perfil)
    return jsonify({'message': 'Perfil não encontrado'}), 404

@app.route('/api/pedidos/historico', methods=['GET'])
@token_required
def get_historico_pedidos(current_user):
    if current_user['tipo'] != 'cliente':
        return jsonify({'message': 'Acesso negado'}), 403

    dao = PedidoDAO()
    historico = dao.listar_por_cliente(current_user['id'])
    return jsonify(historico)

@app.route('/api/produtos/estoque-baixo', methods=['GET'])
@token_required
def get_estoque_baixo(current_user):
    if current_user['tipo'] != 'funcionario':
        return jsonify({'message': 'Acesso negado: funcionalidade restrita a funcionários.'}), 403
    
    dao = ProdutoDAO()
    produtos = dao.listar_estoque_baixo()
    return jsonify(produtos)

@app.route('/api/relatorios/vendas-mensal', methods=['GET'])
@token_required
def get_relatorio_vendas(current_user):
    if current_user['tipo'] != 'funcionario':
        return jsonify({'message': 'Acesso negado: funcionalidade restrita a funcionários.'}), 403
    
    dao = RelatorioDAO()
    relatorio = dao.gerar_relatorio_vendas_mensal()

    if relatorio is not None:
        return jsonify(relatorio)
    else:
        return jsonify({'message': 'Erro ao gerar o relatório.'}), 500
    
# Adicione esta rota ao final do arquivo app.py

@app.route('/api/funcionarios/registrar', methods=['POST'])
@token_required
def registrar_funcionario_api(current_user):
    # Camada de segurança: Apenas funcionários podem acessar
    if current_user['tipo'] != 'funcionario':
        return jsonify({'message': 'Acesso negado.'}), 403

    dados = request.get_json()
    if not dados or not dados.get('email') or not dados.get('senha') or not dados.get('nome'):
        return jsonify({'message': 'Dados essenciais (nome, email, senha) são obrigatórios.'}), 400
    
    dao = FuncionarioDAO()
    resultado = dao.registrar(dados)

    if isinstance(resultado, int):
        return jsonify({'message': 'Funcionário registrado com sucesso!', 'id_funcionario': resultado}), 201
    elif isinstance(resultado, str):
        return jsonify({'message': resultado}), 409
    else:
        return jsonify({'message': 'Erro no servidor ao registrar funcionário.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)