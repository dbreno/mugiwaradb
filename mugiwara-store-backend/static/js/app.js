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
            showModal: false, // Controla a visibilidade do modal de adicionar/editar.
            isEditMode: false, // Define se o modal está em modo de edição ou criação.
            // Objeto que armazena os dados do produto que está sendo criado ou editado no modal.
            currentProduct: {
                id_produto: null,
                nome: '',
                descricao: '',
                preco: 0.01,
                quantidade_estoque: 1,
                categoria: '',
                fabricado_em_mari: false,
                imagem: '' // Campo para armazenar a URL da imagem.
            },
            searchTerm: '', // Armazena o termo de busca do usuário.
            report: null, // Armazena os dados do relatório de estoque.
            showReport: false, // Controla a visibilidade do card de relatório.
            // Filtros e ordenação
            categoryFilter: '', // Categoria selecionada no filtro.
            sortOption: 'nome_asc', // Opção de ordenação selecionada.
            priceMin: null, // Valor mínimo para o filtro de preço.
            priceMax: null, // Valor máximo para o filtro de preço.
            
            // --- NOVOS DADOS PARA UPLOAD DE IMAGEM ---
            imageUploadMode: 'url', // Controla qual input de imagem é mostrado: 'url' ou 'upload'.
            imageFile: null, // Armazena o objeto do arquivo de imagem selecionado pelo usuário.
        }
    },
    // 'mounted' é um hook do ciclo de vida do Vue. Ele é executado
    // assim que o componente é montado na página.
    mounted() {
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
        // --- NOVA PROPRIEDADE COMPUTADA PARA PREVIEW DA IMAGEM ---
        // Gera a URL para o preview da imagem no modal.
        imagePreview() {
            // Se um arquivo foi selecionado, cria uma URL temporária para ele.
            if (this.imageFile) {
                return URL.createObjectURL(this.imageFile);
            }
            // Se não houver arquivo, mas houver uma URL no campo de texto, usa ela.
            if (this.currentProduct.imagem) {
                return this.currentProduct.imagem;
            }
            // Se não houver nada, não mostra preview.
            return null;
        }
    },
    // 'methods' contém as funções que podemos chamar a partir da nossa interface (eventos de clique, etc.).
    methods: {
        // Busca a lista completa de produtos da API.
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
        // Abre o modal em modo de "Adicionar".
        openAddModal() {
            this.isEditMode = false;
            // Reseta o objeto currentProduct para um estado limpo.
            this.currentProduct = {
                id_produto: null, nome: '', descricao: '', preco: 0.01,
                quantidade_estoque: 1, categoria: '', fabricado_em_mari: false, imagem: ''
            };
            this.imageFile = null; // Limpa qualquer arquivo selecionado anteriormente.
            this.imageUploadMode = 'url'; // Reseta o modo para URL.
            this.showModal = true;
        },
        // Abre o modal em modo de "Editar", preenchendo com os dados do produto.
        openEditModal(produto) {
            this.isEditMode = true;
            // Cria uma cópia do objeto produto para evitar mutação direta.
            this.currentProduct = { ...produto };
            this.imageFile = null;
            this.imageUploadMode = 'url';
            this.showModal = true;
        },
        // Fecha o modal.
        closeModal() {
            this.showModal = false;
        },
        // --- NOVO MÉTODO PARA LIDAR COM A SELEÇÃO DE ARQUIVO ---
        handleFileUpload(event) {
            // Pega o primeiro arquivo da lista de arquivos selecionados.
            const file = event.target.files[0];
            if (file) {
                this.imageFile = file;
                // Limpa o campo de URL de imagem para dar prioridade ao upload.
                this.currentProduct.imagem = '';
            }
        },
        // --- NOVO MÉTODO PARA FAZER UPLOAD DA IMAGEM ---
        async uploadImage() {
            // Cria um objeto FormData, que é o formato necessário para enviar arquivos via HTTP.
            const formData = new FormData();
            formData.append('file', this.imageFile); // Adiciona o arquivo ao FormData.

            try {
                // Envia a requisição POST para a nova rota de upload.
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.mensagem || 'Falha no upload da imagem.');
                }
                // Se o upload for bem-sucedido, retorna o caminho do arquivo no servidor.
                return result.filepath;
            } catch (error) {
                console.error('Erro no upload:', error);
                alert(`Erro no upload: ${error.message}`);
                return null; // Retorna null em caso de erro.
            }
        },
        // --- MÉTODO saveProduct ATUALIZADO ---
        async saveProduct() {
            // Validações simples no frontend.
            if (this.currentProduct.preco <= 0) {
                alert('O preço deve ser maior que zero!');
                return;
            }
            if (this.currentProduct.quantidade_estoque < 0) {
                alert('A quantidade em estoque não pode ser negativa!');
                return;
            }

            // 1. Lógica de Upload: Se estiver no modo 'upload' e um arquivo foi selecionado.
            if (this.imageUploadMode === 'upload' && this.imageFile) {
                const imagePath = await this.uploadImage(); // Chama a função de upload.
                if (imagePath) {
                    this.currentProduct.imagem = imagePath; // Atualiza o produto com o caminho da imagem.
                } else {
                    return; // Interrompe o salvamento se o upload falhar.
                }
            }
            
            // 2. Lógica de Salvar Produto (Criar ou Atualizar)
            // Define a URL e o método HTTP com base no modo (edição ou criação).
            const url = this.isEditMode ? `${this.apiUrl}/${this.currentProduct.id_produto}` : this.apiUrl;
            const method = this.isEditMode ? 'PUT' : 'POST';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.currentProduct)
                });
                if (!response.ok) throw new Error('Falha ao salvar o produto.');
                
                await this.fetchProdutos(); // Recarrega a lista de produtos.
                this.closeModal(); // Fecha o modal.
            } catch (error) {
                console.error('Erro ao salvar produto:', error);
                alert('Erro ao salvar produto.');
            }
        },
        // Deleta um produto.
        async deleteProduct(id, nome) {
            if (confirm(`Tem certeza que quer jogar o tesouro "${nome}" no mar?`)) {
                try {
                    const response = await fetch(`${this.apiUrl}/${id}`, { method: 'DELETE' });
                    if (!response.ok) throw new Error('Falha ao deletar produto.');
                    await this.fetchProdutos();
                } catch (error) {
                    console.error('Erro ao deletar produto:', error);
                    alert('Erro ao deletar produto.');
                }
            }
        },
        // Busca produtos com base no termo de busca.
        async searchProdutos() {
            // Se a busca estiver vazia, apenas recarrega todos os produtos.
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
        // Busca os dados para o relatório de estoque.
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
        }
    }
}).mount('#app') // Monta a instância do Vue no elemento com id="app".