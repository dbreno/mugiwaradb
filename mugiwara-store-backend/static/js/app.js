const { createApp } = Vue

createApp({
    data() {
        return {
            produtos: [],
            loading: true,
            error: null,
            apiUrl: '/api/produtos',
            showModal: false,
            isEditMode: false,
            currentProduct: {
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0.01,
                quantidade_estoque: 1,
                categoria: '',
                fabricado_em_mari: false,
                imagem: ''  // Novo campo para URL da imagem
            },
            searchTerm: '',
            report: null,
            showReport: false,
            // NOVOS para filtros
            categoryFilter: '',
            sortOption: 'nome_asc',
            priceMin: null,
            priceMax: null
        }
    },
    mounted() {
        this.fetchProdutos();
        setTimeout(() => {
            document.querySelectorAll('.card-bg').forEach(card => {
                card.classList.add('animate-fadeIn');
            });
        }, 100);
    },
    computed: {
        // NOVO: Categorias únicas para o select
        uniqueCategories() {
            const categories = this.produtos.map(p => p.categoria);
            return [...new Set(categories)].sort();
        },
        // NOVO: Produtos filtrados e ordenados
        filteredProdutos() {
            let filtered = this.produtos;

            // Filtro por categoria
            if (this.categoryFilter) {
                filtered = filtered.filter(p => p.categoria === this.categoryFilter);
            }

            // Filtro por faixa de preço
            if (this.priceMin !== null) {
                filtered = filtered.filter(p => p.preco >= this.priceMin);
            }
            if (this.priceMax !== null) {
                filtered = filtered.filter(p => p.preco <= this.priceMax);
            }

            // Ordenação
            switch (this.sortOption) {
                case 'nome_asc':
                    return filtered.sort((a, b) => a.nome.localeCompare(b.nome));
                case 'nome_desc':
                    return filtered.sort((a, b) => b.nome.localeCompare(a.nome));
                case 'preco_asc':
                    return filtered.sort((a, b) => a.preco - b.preco);
                case 'preco_desc':
                    return filtered.sort((a, b) => b.preco - a.preco);
                default:
                    return filtered;
            }
        }
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
                fabricado_em_mari: false,
                imagem: ''  // Novo
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
        searchProdutos() {
            if (!this.searchTerm) {
                this.fetchProdutos();
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