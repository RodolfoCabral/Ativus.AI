    let assetsData = {
        filiais: [],
        setores: [],
        equipamentos: []
    };

    // Carregar dados ao inicializar
    loadAssetsData();

    // Tornar função global para o botão "Tentar novamente"
    window.loadAssetsData = loadAssetsData;

    async function loadAssetsData() {
        try {
            showLoading();
            
            console.log('Carregando dados dos ativos...');
            
            // Carregar todos os dados em paralelo
            const [filiaisResponse, setoresResponse, equipamentosResponse] = await Promise.all([
                fetch('/api/filiais'),
                fetch('/api/setores'),
                fetch('/api/equipamentos')
            ]);

            console.log('Respostas recebidas:', {
                filiais: filiaisResponse.status,
                setores: setoresResponse.status,
                equipamentos: equipamentosResponse.status
            });

            if (filiaisResponse.ok) {
                const filiaisData = await filiaisResponse.json();
                console.log('Dados de filiais:', filiaisData);
                if (filiaisData.success) {
                    assetsData.filiais = filiaisData.filiais || [];
                }
            } else {
                console.error('Erro na API de filiais:', filiaisResponse.status);
            }

            if (setoresResponse.ok) {
                const setoresData = await setoresResponse.json();
                console.log('Dados de setores:', setoresData);
                if (setoresData.success) {
                    assetsData.setores = setoresData.setores || [];
                }
            } else {
                console.error('Erro na API de setores:', setoresResponse.status);
            }

            if (equipamentosResponse.ok) {
                const equipamentosData = await equipamentosResponse.json();
                console.log('Dados de equipamentos:', equipamentosData);
                if (equipamentosData.success) {
                    assetsData.equipamentos = equipamentosData.equipamentos || [];
                }
            } else {
                console.error('Erro na API de equipamentos:', equipamentosResponse.status);
            }

            console.log('Dados finais carregados:', assetsData);

            // Renderizar árvore
            renderTree();
            updateCounters(); // IMPORTANTE: Usar updateCounters em vez de updateStats

        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            showError('Erro ao carregar dados dos ativos');
        }
    }

    function showLoading() {
        const treeContent = document.getElementById('tree-content');
        treeContent.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Carregando estrutura de ativos...</p>
            </div>
        `;
    }

    function showError(message) {
        const treeContent = document.getElementById('tree-content');
        treeContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button onclick="loadAssetsData()" class="btn btn-primary" style="margin-top: 16px;">
                    <i class="fas fa-redo"></i> Tentar Novamente
                </button>
            </div>
        `;
    }

    function showEmpty() {
        const treeContent = document.getElementById('tree-content');
        treeContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-sitemap"></i>
                <p>Nenhum ativo cadastrado</p>
                <p style="font-size: 14px; color: #999; margin-top: 8px;">
                    Comece cadastrando filiais, setores e equipamentos
                </p>
                <a href="/cadastro-ativos" class="btn btn-primary" style="margin-top: 16px;">
                    <i class="fas fa-plus"></i> Cadastrar Ativos
                </a>
            </div>
        `;
    }

    function renderTree() {
        const treeContent = document.getElementById('tree-content');
        
        if (assetsData.filiais.length === 0) {
            showEmpty();
            return;
        }

        let treeHtml = '';
        
        // Renderizar filiais
        assetsData.filiais.forEach(filial => {
            treeHtml += renderFilial(filial);
        });
        
        treeContent.innerHTML = treeHtml;

        // Adicionar event listeners para expansão/colapso
        addTreeEventListeners();
    }

    function renderFilial(filial) {
        const setoresFilial = assetsData.setores.filter(setor => setor.filial_id === filial.id);
        
        let html = `
            <div class="tree-item" data-type="filial" data-id="${filial.id}">
                <div class="tree-item-header">
                    ${setoresFilial.length > 0 ? '<button class="tree-toggle">-</button>' : '<div style="width: 20px;"></div>'}
                    <div class="tree-icon filial">
                        <i class="fas fa-industry"></i>
                    </div>
                    <div class="tree-label">
                        <span class="tree-tag">${filial.tag}</span>
                        <span class="tree-description">${filial.descricao}</span>
                    </div>
                    <div class="tree-actions">
                        <button class="tree-action" onclick="showAssetInfo('filial', ${filial.id})" title="Informações">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="tree-action" onclick="editAsset('filial', ${filial.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="tree-action" onclick="deleteAsset('filial', ${filial.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>`;
        
        if (setoresFilial.length > 0) {
            html += '<div class="tree-children">';
            setoresFilial.forEach(setor => {
                html += renderSetor(setor);
            });
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }

    function renderSetor(setor) {
        const equipamentosSetor = assetsData.equipamentos.filter(eq => eq.setor_id === setor.id);
        
        let html = `
            <div class="tree-item" data-type="setor" data-id="${setor.id}">
                <div class="tree-item-header">
                    ${equipamentosSetor.length > 0 ? '<button class="tree-toggle">-</button>' : '<div style="width: 20px;"></div>'}
                    <div class="tree-icon setor">
                        <i class="fas fa-circle"></i>
                    </div>
                    <div class="tree-label">
                        <span class="tree-tag">${setor.tag}</span>
                        <span class="tree-description">${setor.descricao}</span>
                    </div>
                    <div class="tree-actions">
                        <button class="tree-action" onclick="showAssetInfo('setor', ${setor.id})" title="Informações">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="tree-action" onclick="editAsset('setor', ${setor.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="tree-action" onclick="deleteAsset('setor', ${setor.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>`;
        
        if (equipamentosSetor.length > 0) {
            html += '<div class="tree-children">';
            equipamentosSetor.forEach(equipamento => {
                html += renderEquipamento(equipamento);
            });
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }

    function renderEquipamento(equipamento) {
        return `
            <div class="tree-item" data-type="equipamento" data-id="${equipamento.id}">
                <div class="tree-item-header">
                    <div style="width: 20px;"></div>
                    <div class="tree-icon equipamento">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="tree-label">
                        <span class="tree-tag">${equipamento.tag}</span>
                        <span class="tree-description">${equipamento.descricao}</span>
                    </div>
                    <div class="tree-actions">
                        <button class="tree-action" onclick="showAssetInfo('equipamento', ${equipamento.id})" title="Informações">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="tree-action" onclick="editAsset('equipamento', ${equipamento.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="tree-action" onclick="deleteAsset('equipamento', ${equipamento.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function addTreeEventListeners() {
        // Adicionar event listeners para os botões de toggle
        document.querySelectorAll('.tree-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                
                const treeItem = this.closest('.tree-item');
                const children = treeItem.querySelector('.tree-children');
                
                if (children) {
                    const isCurrentlyVisible = children.style.display !== 'none' && children.style.display !== '';
                    
                    if (isCurrentlyVisible) {
                        // Colapsar
                        children.style.display = 'none';
                        this.textContent = '+';
                        this.title = 'Expandir';
                    } else {
                        // Expandir
                        children.style.display = 'block';
                        this.textContent = '-';
                        this.title = 'Colapsar';
                    }
                }
            });
        });
        
        // Inicializar estado dos botões
        document.querySelectorAll('.tree-children').forEach(children => {
            children.style.display = 'block'; // Mostrar por padrão
        });
        
        document.querySelectorAll('.tree-toggle').forEach(toggle => {
            toggle.textContent = '-';
            toggle.title = 'Colapsar';
        });
    }
    
    function updateCounters() {
        document.getElementById('filiais-count').textContent = assetsData.filiais.length;
        document.getElementById('setores-count').textContent = assetsData.setores.length;
        document.getElementById('equipamentos-count').textContent = assetsData.equipamentos.length;
    }

    // Funções globais para ações dos botões
    window.showAssetInfo = function(type, id) {
        let asset;
        switch(type) {
            case 'filial':
                asset = assetsData.filiais.find(f => f.id === id);
                break;
            case 'setor':
                asset = assetsData.setores.find(s => s.id === id);
                break;
            case 'equipamento':
                asset = assetsData.equipamentos.find(e => e.id === id);
                break;
        }

        if (asset) {
            showAssetModal(type, asset);
        }
    };

    // IMPORTANTE: Implementação corrigida da função deleteAsset
    window.deleteAsset = async function(type, id) {
        try {
            console.log(`Iniciando exclusão de ${type} com ID ${id}`);
            
            // Verificar permissões (apenas admin e master podem excluir)
            const userProfile = await getCurrentUserProfile();
            console.log(`Perfil do usuário: ${userProfile}`);
            
            if (!userProfile || (userProfile !== 'admin' && userProfile !== 'master')) {
                alert('Apenas administradores podem excluir ativos.');
                return;
            }
            
            // Buscar dados do ativo para mostrar informações na confirmação
            console.log(`Buscando dados do ${type} com ID ${id}`);
            let asset;
            
            switch(type) {
                case 'filial':
                    asset = assetsData.filiais.find(f => f.id === id);
                    break;
                case 'setor':
                    asset = assetsData.setores.find(s => s.id === id);
                    break;
                case 'equipamento':
                    asset = assetsData.equipamentos.find(e => e.id === id);
                    break;
            }
            
            if (!asset) {
                alert(`${type.charAt(0).toUpperCase() + type.slice(1)} não encontrado(a).`);
                return;
            }
            
            let confirmMessage = `⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\n`;
            confirmMessage += `Deseja excluir permanentemente da base de dados:\n`;
            confirmMessage += `${type.toUpperCase()}: ${asset.tag} - ${asset.descricao}\n\n`;
            
            // Adicionar aviso sobre dependentes
            if (type === 'filial') {
                confirmMessage += `⚠️ AVISO: Todos os setores e equipamentos desta filial também serão excluídos!\n\n`;
            } else if (type === 'setor') {
                confirmMessage += `⚠️ AVISO: Todos os equipamentos deste setor também serão excluídos!\n\n`;
            }
            
            confirmMessage += `Confirma a exclusão?`;
            
            console.log(`Solicitando confirmação do usuário`);
            if (!confirm(confirmMessage)) {
                console.log(`Usuário cancelou a exclusão`);
                return;
            }
            
            // Confirmação adicional para filiais e setores
            if (type === 'filial' || type === 'setor') {
                console.log(`Solicitando confirmação adicional para ${type}`);
                if (!confirm(`Confirma novamente? Esta ação removerá TODOS os dados relacionados!`)) {
                    console.log(`Usuário cancelou a exclusão na confirmação adicional`);
                    return;
                }
            }
            
            // Executar exclusão
            console.log(`Enviando requisição DELETE para /api/${type}es/${id}`);
            
            // Mostrar indicador de carregamento
            const loadingModal = showLoadingModal(`Excluindo ${type}...`);
            
            try {
                function getApiPath(type, id) {
                    switch (type) {
                        case 'filial': return `/api/filiais/${id}`;
                        case 'setor': return `/api/setores/${id}`;
                        case 'equipamento': return `/api/equipamentos/${id}`;
                        default: throw new Error(`Tipo de ativo desconhecido: ${type}`);
                    }
                };
                
                // Fechar indicador de carregamento
                closeLoadingModal(loadingModal);
                
                // Verificar status da resposta
                if (!deleteResponse.ok) {
                    const errorText = await deleteResponse.text();
                    console.error(`Erro na resposta da API (${deleteResponse.status}):`, errorText);
                    throw new Error(`Erro ${deleteResponse.status}: ${errorText || 'Falha na comunicação com o servidor'}`);
                }
                
                // Tentar processar a resposta como JSON
                let deleteData;
                try {
                    deleteData = await deleteResponse.json();
                } catch (jsonError) {
                    console.error('Erro ao processar JSON da resposta:', jsonError);
                    const responseText = await deleteResponse.text();
                    throw new Error(`Resposta inválida do servidor: ${responseText}`);
                }
                
                console.log(`Resposta da exclusão:`, deleteData);
                
                if (deleteData.success) {
                    alert(deleteData.message || `${type.charAt(0).toUpperCase() + type.slice(1)} excluído(a) com sucesso!`);
                    // Recarregar dados da árvore
                    console.log(`Recarregando dados da árvore`);
                    loadAssetsData();
                } else {
                    alert('Erro ao excluir: ' + (deleteData.message || 'Erro desconhecido'));
                }
            } catch (fetchError) {
                // Fechar indicador de carregamento se ainda estiver aberto
                closeLoadingModal(loadingModal);
                
                console.error('Erro na requisição de exclusão:', fetchError);
                alert(`Erro ao excluir ${type}: ${fetchError.message}`);
            }
            
        } catch (error) {
            console.error('Erro ao excluir ativo:', error);
            alert(`Erro ao excluir ${type}: ${error.message || 'Erro desconhecido'}`);
        }
    };
    
    // Funções auxiliares para indicador de carregamento
    function showLoadingModal(message) {
        const modal = document.createElement('div');
        modal.className = 'loading-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '9999';
        
        const content = document.createElement('div');
        content.style.backgroundColor = 'white';
        content.style.padding = '20px';
        content.style.borderRadius = '8px';
        content.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
        content.style.textAlign = 'center';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.style.display = 'inline-block';
        spinner.style.width = '30px';
        spinner.style.height = '30px';
        spinner.style.border = '3px solid #f3f3f3';
        spinner.style.borderTop = '3px solid #3498db';
        spinner.style.borderRadius = '50%';
        spinner.style.animation = 'spin 1s linear infinite';
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        
        const text = document.createElement('p');
        text.textContent = message || 'Carregando...';
        text.style.marginTop = '10px';
        
        content.appendChild(spinner);
        content.appendChild(text);
        modal.appendChild(content);
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        return modal;
    }
    
    function closeLoadingModal(modal) {
        if (modal && document.body.contains(modal)) {
            document.body.removeChild(modal);
        }
    }

    function showAssetModal(type, asset) {
        let content = '';
        
        switch(type) {
            case 'filial':
                content = `
                    <h3><i class="fas fa-industry"></i> ${asset.tag}</h3>
                    <p><strong>Descrição:</strong> ${asset.descricao}</p>
                    <p><strong>Endereço:</strong> ${asset.endereco}</p>
                    <p><strong>Cidade:</strong> ${asset.cidade} - ${asset.estado}</p>
                    <p><strong>E-mail:</strong> ${asset.email}</p>
                    <p><strong>Telefone:</strong> ${asset.telefone}</p>
                    <p><strong>CNPJ:</strong> ${asset.cnpj}</p>
                    <p><strong>Empresa:</strong> ${asset.empresa}</p>
                    <p><strong>Criado por:</strong> ${asset.usuario_criacao}</p>
                    <p><strong>Data de criação:</strong> ${new Date(asset.data_criacao).toLocaleString('pt-BR')}</p>
                `;
                break;
            case 'setor':
                content = `
                    <h3><i class="fas fa-circle"></i> ${asset.tag}</h3>
                    <p><strong>Descrição:</strong> ${asset.descricao}</p>
                    <p><strong>Filial:</strong> ${assetsData.filiais.find(f => f.id === asset.filial_id)?.tag || 'N/A'}</p>
                    <p><strong>Empresa:</strong> ${asset.empresa}</p>
                    <p><strong>Criado por:</strong> ${asset.usuario_criacao}</p>
                    <p><strong>Data de criação:</strong> ${new Date(asset.data_criacao).toLocaleString('pt-BR')}</p>
                `;
                break;
            case 'equipamento':
                content = `
                    <h3><i class="fas fa-check-circle"></i> ${asset.tag}</h3>
                    <p><strong>Descrição:</strong> ${asset.descricao}</p>
                    <p><strong>Setor:</strong> ${assetsData.setores.find(s => s.id === asset.setor_id)?.tag || 'N/A'}</p>
                    <p><strong>Empresa:</strong> ${asset.empresa}</p>
                    <p><strong>Criado por:</strong> ${asset.usuario_criacao}</p>
                    <p><strong>Data de criação:</strong> ${new Date(asset.data_criacao).toLocaleString('pt-BR')}</p>
                `;
                break;
        }

        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Informações do Ativo</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        // Adicionar ao body
        document.body.appendChild(modal);

        // Mostrar modal
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Fechar modal
        modal.querySelector('.close-btn').addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        });
    }

    // IMPORTANTE: Implementação corrigida da função editAsset
    window.editAsset = async function(type, id) {
        try {
            console.log(`Iniciando edição de ${type} com ID ${id}`);
            
            // Verificar permissões (apenas admin e master podem editar)
            const userProfile = await getCurrentUserProfile();
            console.log(`Perfil do usuário: ${userProfile}`);
            
            if (!userProfile || (userProfile !== 'admin' && userProfile !== 'master')) {
                alert('Apenas administradores podem editar ativos.');
                return;
            }
            
            // Buscar dados do ativo
            let asset;
            
            switch(type) {
                case 'filial':
                    asset = assetsData.filiais.find(f => f.id === id);
                    break;
                case 'setor':
                    asset = assetsData.setores.find(s => s.id === id);
                    break;
                case 'equipamento':
                    asset = assetsData.equipamentos.find(e => e.id === id);
                    break;
            }
            
            if (!asset) {
                alert(`${type.charAt(0).toUpperCase() + type.slice(1)} não encontrado(a).`);
                return;
            }
            
            // Abrir modal de edição baseado no tipo
            console.log(`Abrindo modal de edição para ${type}`);
            switch(type) {
                case 'filial':
                    openEditFilialModal(asset);
                    break;
                case 'setor':
                    openEditSetorModal(asset);
                    break;
                case 'equipamento':
                    openEditEquipamentoModal(asset);
                    break;
            }
            
        } catch (error) {
            console.error('Erro ao editar ativo:', error);
            alert('Erro ao carregar dados para edição.');
        }
    };

    let currentUserProfile = '';
    let currentUserCompany = '';
    
    async function getCurrentUserProfile() {
        console.log('Obtendo perfil do usuário...');
        
        if (currentUserProfile) {
            console.log(`Perfil já em cache: ${currentUserProfile}`);
            return currentUserProfile;
        }
        
        try {
            console.log('Fazendo requisição para /api/user');
            const response = await fetch('/api/user');
            
            if (!response.ok) {
                console.error(`Erro na API de usuário: ${response.status}`);
                return 'user'; // Fallback
            }
            
            const data = await response.json();
            console.log('Resposta da API de usuário:', data);
            
            if (data.success && data.user) {
                currentUserProfile = data.user.profile;
                currentUserCompany = data.user.company;
                console.log(`Perfil obtido: ${currentUserProfile}, Empresa: ${currentUserCompany}`);
                return currentUserProfile;
            } else {
                console.error('Erro na resposta da API:', data);
            }
        } catch (error) {
            console.error('Erro ao obter perfil do usuário:', error);
        }
        
        console.log('Usando perfil padrão: user');
        return 'user'; // Fallback
    }
    
    // ==================== MODAIS DE EDIÇÃO ====================
    
    function openEditFilialModal(filial) {
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Editar Filial</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="edit-filial-form">
                        <div class="form-group">
                            <label for="tag">Tag</label>
                            <input type="text" id="tag" name="tag" value="${filial.tag}" required>
                        </div>
                        <div class="form-group">
                            <label for="descricao">Descrição</label>
                            <input type="text" id="descricao" name="descricao" value="${filial.descricao}" required>
                        </div>
                        <div class="form-group">
                            <label for="endereco">Endereço</label>
                            <input type="text" id="endereco" name="endereco" value="${filial.endereco}" required>
                        </div>
                        <div class="form-group">
                            <label for="cidade">Cidade</label>
                            <input type="text" id="cidade" name="cidade" value="${filial.cidade}" required>
                        </div>
                        <div class="form-group">
                            <label for="estado">Estado</label>
                            <input type="text" id="estado" name="estado" value="${filial.estado}" required>
                        </div>
                        <div class="form-group">
                            <label for="email">E-mail</label>
                            <input type="email" id="email" name="email" value="${filial.email}" required>
                        </div>
                        <div class="form-group">
                            <label for="telefone">Telefone</label>
                            <input type="text" id="telefone" name="telefone" value="${filial.telefone}" required>
                        </div>
                        <div class="form-group">
                            <label for="cnpj">CNPJ</label>
                            <input type="text" id="cnpj" name="cnpj" value="${filial.cnpj}" required>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary close-modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Salvar Alterações</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Adicionar ao body
        document.body.appendChild(modal);

        // Mostrar modal
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Fechar modal
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        };

        modal.querySelector('.close-btn').addEventListener('click', closeModal);
        modal.querySelector('.close-modal').addEventListener('click', closeModal);

        // Submeter formulário
        modal.querySelector('#edit-filial-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                tag: modal.querySelector('#tag').value,
                descricao: modal.querySelector('#descricao').value,
                endereco: modal.querySelector('#endereco').value,
                cidade: modal.querySelector('#cidade').value,
                estado: modal.querySelector('#estado').value,
                email: modal.querySelector('#email').value,
                telefone: modal.querySelector('#telefone').value,
                cnpj: modal.querySelector('#cnpj').value
            };
            
            try {
                const loadingModal = showLoadingModal('Salvando alterações...');
                
                const response = await fetch(`/api/filiais/${filial.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                closeLoadingModal(loadingModal);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Erro ${response.status}: ${errorText || 'Falha na comunicação com o servidor'}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message || 'Filial atualizada com sucesso!');
                    closeModal();
                    loadAssetsData(); // Recarregar dados
                } else {
                    alert('Erro ao salvar: ' + (data.message || 'Erro desconhecido'));
                }
            } catch (error) {
                console.error('Erro ao salvar filial:', error);
                alert('Erro ao salvar alterações: ' + error.message);
            }
        });
    }
    
    function openEditSetorModal(setor) {
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Editar Setor</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="edit-setor-form">
                        <div class="form-group">
                            <label for="tag">Tag</label>
                            <input type="text" id="tag" name="tag" value="${setor.tag}" required>
                        </div>
                        <div class="form-group">
                            <label for="descricao">Descrição</label>
                            <input type="text" id="descricao" name="descricao" value="${setor.descricao}" required>
                        </div>
                        <div class="form-group">
                            <label for="filial_id">Filial</label>
                            <select id="filial_id" name="filial_id" required>
                                ${assetsData.filiais.map(f => `<option value="${f.id}" ${f.id === setor.filial_id ? 'selected' : ''}>${f.tag} - ${f.descricao}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary close-modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Salvar Alterações</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Adicionar ao body
        document.body.appendChild(modal);

        // Mostrar modal
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Fechar modal
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        };

        modal.querySelector('.close-btn').addEventListener('click', closeModal);
        modal.querySelector('.close-modal').addEventListener('click', closeModal);

        // Submeter formulário
        modal.querySelector('#edit-setor-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                tag: modal.querySelector('#tag').value,
                descricao: modal.querySelector('#descricao').value,
                filial_id: parseInt(modal.querySelector('#filial_id').value)
            };
            
            try {
                const loadingModal = showLoadingModal('Salvando alterações...');
                
                const response = await fetch(`/api/setores/${setor.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                closeLoadingModal(loadingModal);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Erro ${response.status}: ${errorText || 'Falha na comunicação com o servidor'}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message || 'Setor atualizado com sucesso!');
                    closeModal();
                    loadAssetsData(); // Recarregar dados
                } else {
                    alert('Erro ao salvar: ' + (data.message || 'Erro desconhecido'));
                }
            } catch (error) {
                console.error('Erro ao salvar setor:', error);
                alert('Erro ao salvar alterações: ' + error.message);
            }
        });
    }
    
    function openEditEquipamentoModal(equipamento) {
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Editar Equipamento</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="edit-equipamento-form">
                        <div class="form-group">
                            <label for="tag">Tag</label>
                            <input type="text" id="tag" name="tag" value="${equipamento.tag}" required>
                        </div>
                        <div class="form-group">
                            <label for="descricao">Descrição</label>
                            <input type="text" id="descricao" name="descricao" value="${equipamento.descricao}" required>
                        </div>
                        <div class="form-group">
                            <label for="setor_id">Setor</label>
                            <select id="setor_id" name="setor_id" required>
                                ${assetsData.setores.map(s => `<option value="${s.id}" ${s.id === equipamento.setor_id ? 'selected' : ''}>${s.tag} - ${s.descricao}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary close-modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Salvar Alterações</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Adicionar ao body
        document.body.appendChild(modal);

        // Mostrar modal
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Fechar modal
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        };

        modal.querySelector('.close-btn').addEventListener('click', closeModal);
        modal.querySelector('.close-modal').addEventListener('click', closeModal);

        // Submeter formulário
        modal.querySelector('#edit-equipamento-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                tag: modal.querySelector('#tag').value,
                descricao: modal.querySelector('#descricao').value,
                setor_id: parseInt(modal.querySelector('#setor_id').value)
            };
            
            try {
                const loadingModal = showLoadingModal('Salvando alterações...');
                
                const response = await fetch(`/api/equipamentos/${equipamento.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                closeLoadingModal(loadingModal);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Erro ${response.status}: ${errorText || 'Falha na comunicação com o servidor'}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message || 'Equipamento atualizado com sucesso!');
                    closeModal();
                    loadAssetsData(); // Recarregar dados
                } else {
                    alert('Erro ao salvar: ' + (data.message || 'Erro desconhecido'));
                }
            } catch (error) {
                console.error('Erro ao salvar equipamento:', error);
                alert('Erro ao salvar alterações: ' + error.message);
            }
        });
    }

