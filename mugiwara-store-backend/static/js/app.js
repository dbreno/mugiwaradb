const { createApp } = Vue

createApp({
    data() {
        return {
            produtos: [],
            loading: true,
            error: null,
            apiUrl: '/api/produtos',  // Alterado para relativo, já que Flask serve tudo
            showModal: false,
            isEditMode: false,
            currentProduct: {
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0,
                quantidade_estoque: 0,
                categoria: '',
                fabricado_em_mari: false
            },
            // NOVOS: Para busca e relatório
            searchTerm: '',
            report: null,
            showReport: false
        }
    },
    mounted() {
        this.fetchProdutos();
    },
    methods: {
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
        openAddModal() {
            this.isEditMode = false;
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
            this.currentProduct = { ...produto };
            this.showModal = true;
        },
        closeModal() {
            this.showModal = false;
        },
        saveProduct() {
            // NOVO: Validações no frontend
            if (this.currentProduct.preco <= 0) {
                alert('O preço deve ser maior que zero!');
                return;
            }
            if (this.currentProduct.quantidade_estoque < 0) {
                alert('A quantidade em estoque não pode ser negativa!');
                return;
            }

            if (this.isEditMode) {
                fetch(`${this.apiUrl}/${this.currentProduct.id_produto}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.currentProduct)
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos();
                    this.closeModal();
                })
                .catch(error => console.error('Erro ao atualizar produto:', error));
            } else {
                fetch(this.apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.currentProduct)
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos();
                    this.closeModal();
                })
                .catch(error => console.error('Erro ao adicionar produto:', error));
            }
        },
        deleteProduct(id, nome) {
            if (confirm(`Tem certeza que quer jogar o tesouro "${nome}" no mar?`)) {
                fetch(`${this.apiUrl}/${id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(() => {
                    this.fetchProdutos();
                })
                .catch(error => console.error('Erro ao deletar produto:', error));
            }
        },
        // NOVO: Método para busca
        searchProdutos() {
            if (!this.searchTerm) {
                this.fetchProdutos();  // Se vazio, volta para todos
                return;
            }
            this.loading = true;
            fetch(`/api/produtos/buscar?nome=${encodeURIComponent(this.searchTerm)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Falha na busca!');
                    }
                    return response.json();
                })
                .then(data => {
                    this.produtos = data;
                })
                .catch(error => {
                    console.error('Erro na busca:', error);
                    this.error = error.message;
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        // NOVO: Método para relatório
        fetchReport() {
            fetch('/api/produtos/relatorio')
                .then(response => response.json())
                .then(data => {
                    this.report = data;
                    this.showReport = true;
                })
                .catch(error => console.error('Erro ao carregar relatório:', error));
        }
    }
}).mount('#app')