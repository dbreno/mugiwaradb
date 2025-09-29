// Inicializa a aplicação Vue.js
const { createApp } = Vue

createApp({
    // 'data' é uma função que retorna o estado inicial da nossa aplicação.
    // Todas as variáveis reativas vivem aqui.
    data() {
        return {
            produtos: [], // Array para armazenar a lista de produtos vinda da API.
            loading: true, // Booleano para controlar a exibição da mensagem de "carregando".
            error: null, // String para armazenar mensagens de erro.
            apiUrl: '/api/produtos', // URL base da nossa API de produtos.
            showModal: false, // Controla a visibilidade do modal de adicionar/editar produto.
            isEditMode: false, // Define se o modal de produto está em modo de edição ou criação.
            // Objeto que armazena os dados do produto que está sendo criado ou editado no modal.
            currentProduct: {
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0.01,
                quantidade_estoque: 1,
                categoria: '',
                fabricado_em_mari: false,
                imagem: ''
            },
            searchTerm: '', // Armazena o termo de busca do usuário.
            report: null, // Armazena os dados do relatório de estoque.
            showReport: false, // Controla a visibilidade do card de relatório.
            // Filtros e ordenação
            categoryFilter: '', // Categoria selecionada no filtro.
            sortOption: 'nome_asc', // Opção de ordenação selecionada.
            priceMin: null, // Valor mínimo para o filtro de preço.
            priceMax: null, // Valor máximo para o filtro de preço.
            
            // --- DADOS PARA UPLOAD DE IMAGEM ---
            imageUploadMode: 'url', // Controla qual input de imagem é mostrado: 'url' ou 'upload'.
            imageFile: null, // Armazena o objeto do arquivo de imagem selecionado pelo usuário.
            
            // --- NOVOS DADOS PARA AUTENTICAÇÃO ---
            isLoggedIn: false,        // Controla se o usuário está logado.
            token: null,              // Armazena o token JWT.
            currentUser: null,        // Armazena os dados do usuário logado ({id, tipo}).
            showLoginModal: false,    // Controla a visibilidade do modal de login.
            showRegisterModal: false, // Controla a visibilidade do modal de registro.
            loginForm: {
                email: '',
                senha: ''
            },
            registerForm: {
                nome: '',
                email: '',
                senha: '',
                telefone: '',
                // Objeto aninhado para o endereço
                endereco: {
                    cep: '',
                    logradouro: '',
                    numero_endereco: '',
                    complemento_endereco: '',
                    bairro: '',
                    cidade: '',
                    estado: ''
                },
                torce_flamengo: false,
                assiste_one_piece: false,
                natural_de_sousa: false

            },
            // --- NOVOS DADOS PARA O CARRINHO ---
            cart: [],              // Array para armazenar os itens do carrinho.
            showCartModal: false,  // Controla a visibilidade do modal do carrinho.
            formaPagamento: 'Cartão de Crédito', // Forma de pagamento padrão
            showProfileModal: false,
            userProfile: null,
            showHistoryModal: false,
            orderHistory: []
        }
    },
    // 'mounted' é um hook do ciclo de vida do Vue. Ele é executado
    // assim que o componente é montado na página.
    mounted() {
        this.checkForToken(); // Verifica se já existe um token ao carregar a página.
        this.fetchProdutos(); // Busca os produtos da API assim que a página carrega.
    },
    // 'computed' são propriedades que calculam seu valor com base em outras propriedades.
    // Elas são reativas e se atualizam automaticamente.
    computed: {
        // Gera uma lista de categorias únicas a partir dos produtos existentes para usar no filtro.
        uniqueCategories() {
            const categories = this.produtos.map(p => p.categoria);
            return [...new Set(categories)].sort();
        },
        // A propriedade principal que aplica todos os filtros e ordenações.
        // A interface sempre exibirá o resultado desta função.
        filteredProdutos() {
            let filtered = [...this.produtos]; // Cria uma cópia para não modificar o array original.

            // 1. Filtro por Categoria
            if (this.categoryFilter) {
                filtered = filtered.filter(p => p.categoria === this.categoryFilter);
            }

            // 2. Filtro por Faixa de Preço
            if (this.priceMin !== null && this.priceMin !== '') {
                filtered = filtered.filter(p => p.preco >= this.priceMin);
            }
            if (this.priceMax !== null && this.priceMax !== '') {
                filtered = filtered.filter(p => p.preco <= this.priceMax);
            }

            // 3. Ordenação
            return filtered.sort((a, b) => {
                switch (this.sortOption) {
                    case 'nome_desc': return b.nome.localeCompare(a.nome);
                    case 'preco_asc': return a.preco - b.preco;
                    case 'preco_desc': return b.preco - a.preco;
                    case 'nome_asc':
                    default:
                        return a.nome.localeCompare(b.nome);
                }
            });
        },
        // Gera a URL para o preview da imagem no modal.
        imagePreview() {
            if (this.imageFile) {
                return URL.createObjectURL(this.imageFile);
            }
            if (this.currentProduct.imagem) {
                return this.currentProduct.imagem;
            }
            return null;
        },
        // Verifica se o usuário logado é um funcionário.
        isFuncionario() {
            return this.isLoggedIn && this.currentUser?.tipo === 'funcionario';
        },
        // --- NOVAS COMPUTED PROPERTIES PARA O CARRINHO ---
        cartTotal() {
            // Calcula o valor total dos itens no carrinho.
            return this.cart.reduce((total, item) => total + (item.preco * item.quantidade), 0);
        },
        cartItemCount() {
            // Conta o número total de itens no carrinho.
            return this.cart.reduce((total, item) => total + item.quantidade, 0);
        }
    },
    // 'methods' contém as funções que podemos chamar a partir da nossa interface.
    methods: {
        // --- MÉTODOS DE AUTENTICAÇÃO ---
        checkForToken() {
            const token = localStorage.getItem('authToken');
            if (token) {
                this.token = token;
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    if (payload.exp * 1000 > Date.now()) {
                        // --- LINHA ALTERADA ---
                        // Armazena os dados do usuário, incluindo a flag de desconto
                        this.currentUser = { 
                            id: payload.id, 
                            tipo: payload.tipo, 
                            temDesconto: payload.tem_desconto || false // Garante que o valor seja booleano
                        };
                        this.isLoggedIn = true;
                    } else {
                        this.logout();
                    }
                } catch (e) {
                    console.error("Erro ao decodificar token:", e);
                    this.logout();
                }
            }
        },
        openLoginModal() { this.showLoginModal = true; },
        closeLoginModal() { this.showLoginModal = false; },
        openRegisterModal() { this.showRegisterModal = true; },
        closeRegisterModal() { this.showRegisterModal = false; },

        async login() {
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: this.loginForm.email, senha: this.loginForm.senha })
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || 'Falha no login.');
                
                this.token = data.token;
                localStorage.setItem('authToken', data.token);
                this.checkForToken();
                this.closeLoginModal();
                alert('Bem-vindo a bordo!');
            } catch (error) {
                console.error('Erro no login:', error);
                alert(`Erro: ${error.message}`);
            }
        },

        async register() {
            try {
                // Apenas o objeto registerForm é enviado, o backend sabe como processá-lo
                const response = await fetch('/api/registrar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.registerForm)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.message || 'Falha no registro.');

                this.closeRegisterModal();
                alert('Registro realizado com sucesso! Agora você pode fazer o login.');
                this.openLoginModal();
            } catch (error) {
                console.error('Erro no registro:', error);
                alert(`Erro: ${error.message}`);
            }
        },

         // NOVO MÉTODO PARA BUSCAR ENDEREÇO PELO CEP
        async buscarCep() {
            const cep = this.registerForm.endereco.cep.replace(/\D/g, ''); // Remove caracteres não numéricos
            if (cep.length !== 8) return;

            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                if (!response.ok) throw new Error('CEP não encontrado.');
                const data = await response.json();
                if (data.erro) {
                    alert('CEP não encontrado.');
                    return;
                }
                // Preenche os campos do formulário com os dados do CEP
                this.registerForm.endereco.logradouro = data.logradouro;
                this.registerForm.endereco.bairro = data.bairro;
                this.registerForm.endereco.cidade = data.localidade;
                this.registerForm.endereco.estado = data.uf;
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
                alert(error.message);
            }
        },

        logout() {
            this.isLoggedIn = false;
            this.token = null;
            this.currentUser = null;
            localStorage.removeItem('authToken');
            alert('Até a próxima, marujo!');
        },

        // --- MÉTODOS DE PRODUTO ---
        // Retorna os cabeçalhos necessários para requisições autenticadas.
        getAuthHeaders() {
            return {
                'Content-Type': 'application/json',
                'x-access-token': this.token || ''
            };
        },

        async fetchProdutos() {
            this.loading = true;
            this.error = null;
            try {
                const response = await fetch(this.apiUrl);
                if (!response.ok) throw new Error('Falha ao buscar os tesouros. O Den Den Mushi pode estar fora de alcance!');
                this.produtos = await response.json();
            } catch (error) {
                console.error('Erro:', error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        openAddModal() {
            this.isEditMode = false;
            this.currentProduct = {
                id_produto: null, nome: '', descricao: '', preco: 0.01,
                quantidade_estoque: 1, categoria: '', fabricado_em_mari: false, imagem: ''
            };
            this.imageFile = null;
            this.imageUploadMode = 'url';
            this.showModal = true;
        },

        openEditModal(produto) {
            this.isEditMode = true;
            this.currentProduct = { ...produto };
            this.imageFile = null;
            this.imageUploadMode = 'url';
            this.showModal = true;
        },

        closeModal() {
            this.showModal = false;
        },

        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.imageFile = file;
                this.currentProduct.imagem = '';
            }
        },

        async uploadImage() {
            const formData = new FormData();
            formData.append('file', this.imageFile);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    headers: { 'x-access-token': this.token || '' }, // Protege o upload
                    body: formData
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.message || 'Falha no upload da imagem.');
                }
                return result.filepath;
            } catch (error) {
                console.error('Erro no upload:', error);
                alert(`Erro no upload: ${error.message}`);
                return null;
            }
        },

        async saveProduct() {
            if (this.currentProduct.preco <= 0) {
                alert('O preço deve ser maior que zero!');
                return;
            }
            if (this.currentProduct.quantidade_estoque < 0) {
                alert('A quantidade em estoque não pode ser negativa!');
                return;
            }

            if (this.imageUploadMode === 'upload' && this.imageFile) {
                const imagePath = await this.uploadImage();
                if (imagePath) {
                    this.currentProduct.imagem = imagePath;
                } else {
                    return;
                }
            }
            
            const url = this.isEditMode ? `${this.apiUrl}/${this.currentProduct.id_produto}` : this.apiUrl;
            const method = this.isEditMode ? 'PUT' : 'POST';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: this.getAuthHeaders(), // Envia o token
                    body: JSON.stringify(this.currentProduct)
                });
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.message || 'Falha ao salvar o produto.');
                }
                
                await this.fetchProdutos();
                this.closeModal();
            } catch (error) {
                console.error('Erro ao salvar produto:', error);
                alert(error.message);
            }
        },

        async deleteProduct(id, nome) {
            if (confirm(`Tem certeza que quer jogar o tesouro "${nome}" no mar?`)) {
                try {
                    const response = await fetch(`${this.apiUrl}/${id}`, { 
                        method: 'DELETE',
                        headers: { 'x-access-token': this.token || '' } // Envia o token
                    });
                     if (!response.ok) {
                        const data = await response.json();
                        throw new Error(data.message || 'Falha ao deletar produto.');
                    }
                    await this.fetchProdutos();
                } catch (error) {
                    console.error('Erro ao deletar produto:', error);
                    alert(error.message);
                }
            }
        },

        async searchProdutos() {
            if (!this.searchTerm.trim()) {
                this.fetchProdutos();
                return;
            }
            this.loading = true;
            this.error = null;
            try {
                const response = await fetch(`/api/produtos/buscar?nome=${encodeURIComponent(this.searchTerm)}`);
                if (!response.ok) throw new Error('Falha na busca!');
                this.produtos = await response.json();
            } catch (error) {
                console.error('Erro na busca:', error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        },

        async fetchReport() {
            try {
                const response = await fetch('/api/produtos/relatorio');
                if (!response.ok) throw new Error('Falha ao carregar relatório.');
                this.report = await response.json();
                this.showReport = true;
            } catch (error) {
                console.error('Erro ao carregar relatório:', error);
                alert('Erro ao carregar relatório.');
            }
        },

        // --- NOVOS MÉTODOS PARA O CARRINHO E CHECKOUT ---
        openCartModal() { this.showCartModal = true; },
        closeCartModal() { this.showCartModal = false; },

        addToCart(produto) {
            // Verifica se o usuário é cliente e está logado
            if (!this.isLoggedIn || this.currentUser.tipo !== 'cliente') {
                alert('Você precisa estar logado como cliente para adicionar itens ao carrinho!');
                this.openLoginModal();
                return;
            }

            // Procura se o item já existe no carrinho
            const cartItem = this.cart.find(item => item.id_produto === produto.id_produto);

            if (cartItem) {
                // Se existe, apenas incrementa a quantidade, respeitando o estoque
                if (cartItem.quantidade < produto.quantidade_estoque) {
                    cartItem.quantidade++;
                } else {
                    alert('Você já selecionou a quantidade máxima em estoque!');
                }
            } else {
                // Se não existe, adiciona o produto ao carrinho com quantidade 1
                if (produto.quantidade_estoque > 0) {
                    this.cart.push({ ...produto, quantidade: 1 });
                } else {
                    alert('Este tesouro está esgotado!');
                }
            }
        },
        
        removeFromCart(productId) {
            // Filtra o carrinho, mantendo todos os itens exceto o que foi removido.
            this.cart = this.cart.filter(item => item.id_produto !== productId);
        },

        async checkout() {
            if (this.cart.length === 0) {
                alert('Seu carrinho está vazio!');
                return;
            }

            // Prepara os dados para enviar para a API
            const pedidoData = {
                forma_pagamento: this.formaPagamento,
                itens: this.cart.map(item => ({
                    id_produto: item.id_produto,
                    quantidade: item.quantidade
                }))
            };

            try {
                const response = await fetch('/api/pedidos', {
                    method: 'POST',
                    headers: this.getAuthHeaders(),
                    body: JSON.stringify(pedidoData)
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.mensagem || 'Falha ao finalizar o pedido.');
                }

                alert(`Pedido #${result.id_pedido} realizado com sucesso!`);
                this.cart = []; // Limpa o carrinho
                this.closeCartModal();
                await this.fetchProdutos(); // Atualiza a lista de produtos para refletir o novo estoque

            } catch (error) {
                console.error("Erro no checkout:", error);
                alert(`Erro: ${error.message}`);
            }
        },

        openProfileModal() {
            this.fetchUserProfile(); // Busca os dados ao abrir
            this.showProfileModal = true;
        },
        closeProfileModal() {
            this.showProfileModal = false;
        },
        async fetchUserProfile() {
            try {
                const response = await fetch('/api/cliente/perfil', {
                    headers: this.getAuthHeaders()
                });
                if (!response.ok) throw new Error('Falha ao buscar dados do perfil.');
                this.userProfile = await response.json();
            } catch (error) {
                console.error('Erro:', error);
                alert(error.message);
            }
        },

        openHistoryModal() {
            this.fetchOrderHistory(); // Busca os dados ao abrir
            this.showHistoryModal = true;
        },
        closeHistoryModal() {
            this.showHistoryModal = false;
        },
        async fetchOrderHistory() {
            try {
                const response = await fetch('/api/pedidos/historico', {
                    headers: this.getAuthHeaders()
                });
                if (!response.ok) throw new Error('Falha ao buscar histórico de pedidos.');
                this.orderHistory = await response.json();
            } catch (error) {
                console.error('Erro:', error);
                alert(error.message);
            }
        }

    }
}).mount('#app')