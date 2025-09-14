const { createApp } = Vue

createApp({
    data() {
        return {
            produtos: [],
            loading: true,
            error: null,
            apiUrl: 'http://127.0.0.1:5000/api/produtos',
            // NOVOS DADOS PARA O CRUD
            showModal: false,
            isEditMode: false,
            currentProduct: { // Objeto para o formulário
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0,
                quantidade_estoque: 0,
                categoria: '',
                fabricado_em_mari: false
            }
        }
    },
    mounted() {
        this.fetchProdutos();
    },
    methods: {
        // --- MÉTODOS EXISTENTES ---
        fetchProdutos() {
            this.loading = true;
            this.error = null;
            fetch(this.apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Falha ao buscar os tesouros. O Den Den Mushi pode estar fora de alcance!');
                    }
                    return response.json();
                })
                .then(data => {
                    this.produtos = data;
                })
                .catch(error => {
                    console.error('Erro:', error);
                    this.error = error.message;
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        
        // --- NOVOS MÉTODOS PARA O MODAL ---
        openAddModal() {
            this.isEditMode = false;
            // Limpa o formulário para um novo produto
            this.currentProduct = {
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0.01,
                quantidade_estoque: 1,
                categoria: '',
                fabricado_em_mari: false
            };
            this.showModal = true;
        },
        openEditModal(produto) {
            this.isEditMode = true;
            // Carrega o formulário com os dados do produto a ser editado
            this.currentProduct = { ...produto };
            this.showModal = true;
        },
        closeModal() {
            this.showModal = false;
        },

        // --- NOVOS MÉTODOS PARA O CRUD ---
        saveProduct() {
            if (this.isEditMode) {
                // Lógica de ATUALIZAÇÃO (PUT)
                fetch(`${this.apiUrl}/${this.currentProduct.id_produto}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.currentProduct)
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos(); // Atualiza a lista
                    this.closeModal();
                })
                .catch(error => console.error('Erro ao atualizar produto:', error));
            } else {
                // Lógica de CRIAÇÃO (POST)
                fetch(this.apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.currentProduct)
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos(); // Atualiza a lista
                    this.closeModal();
                })
                .catch(error => console.error('Erro ao adicionar produto:', error));
            }
        },
        deleteProduct(id, nome) {
            // Pede confirmação antes de excluir
            if (confirm(`Tem certeza que quer jogar o tesouro "${nome}" no mar?`)) {
                fetch(`${this.apiUrl}/${id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos(); // Atualiza a lista
                })
                .catch(error => console.error('Erro ao deletar produto:', error));
            }
        }
    }
}).mount('#app')

