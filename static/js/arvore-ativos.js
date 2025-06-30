document.addEventListener('DOMContentLoaded', function() {
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
            updateCounters();
            //updateStats();

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

    function renderFilialNode(filial) {
        const setoresFilial = assetsData.setores.filter(setor => setor.filial_id === filial.id);
        const hasChildren = setoresFilial.length > 0;
        
        let html = `
            <li class="tree-item ${hasChildren ? 'expanded' : ''}" data-type="filial" data-id="${filial.id}">
                ${hasChildren ? '<div class="expand-toggle"></div>' : ''}
                <div class="tree-content">
                    <div class="tree-icon filial-icon">
                        <i class="fas fa-industry"></i>
                    </div>
                    <span class="tree-label">${filial.tag}</span>
                    <span class="tree-description">- ${filial.descricao}</span>
                    <div class="tree-actions">
                        <button class="action-btn info" title="Informações" onclick="showAssetInfo('filial', ${filial.id})">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="action-btn edit" title="Editar" onclick="editAsset('filial', ${filial.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" title="Excluir" onclick="deleteAsset('filial', ${filial.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
        `;

        if (hasChildren) {
            html += '<ul class="tree-children">';
            setoresFilial.forEach(setor => {
                html += renderSetorNode(setor);
            });
            html += '</ul>';
        }

        html += '</li>';
        return html;
    }

    function renderSetorNode(setor) {
        const equipamentosSetor = assetsData.equipamentos.filter(equip => equip.setor_id === setor.id);
        const hasChildren = equipamentosSetor.length > 0;
        
        let html = `
            <li class="tree-item ${hasChildren ? 'expanded' : ''}" data-type="setor" data-id="${setor.id}">
                ${hasChildren ? '<div class="expand-toggle"></div>' : ''}
                <div class="tree-content">
                    <div class="tree-icon setor-icon">
                        <i class="fas fa-circle"></i>
                    </div>
                    <span class="tree-label">${setor.tag}</span>
                    <span class="tree-description">- ${setor.descricao}</span>
                    <div class="tree-actions">
                        <button class="action-btn info" title="Informações" onclick="showAssetInfo('setor', ${setor.id})">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="action-btn edit" title="Editar" onclick="editAsset('setor', ${setor.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" title="Excluir" onclick="deleteAsset('setor', ${setor.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
        `;

        if (hasChildren) {
            html += '<ul class="tree-children">';
            equipamentosSetor.forEach(equipamento => {
                html += renderEquipamentoNode(equipamento);
            });
            html += '</ul>';
        }

        html += '</li>';
        return html;
    }

    function renderEquipamentoNode(equipamento) {
        return `
            <li class="tree-item" data-type="equipamento" data-id="${equipamento.id}">
                <div class="tree-content">
                    <div class="tree-icon equipamento-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <span class="tree-label">${equipamento.tag}</span>
                    <span class="tree-description">- ${equipamento.descricao}</span>
                    <div class="tree-actions">
                        <button class="action-btn info" title="Informações" onclick="showAssetInfo('equipamento', ${equipamento.id})">
                            <i class="fas fa-info"></i>
                        </button>
                        <button class="action-btn edit" title="Editar" onclick="editAsset('equipamento', ${equipamento.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" title="Excluir" onclick="deleteAsset('equipamento', ${equipamento.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </li>
        `;
    }

    function addTreeEventListeners() {
        // Event listeners para expansão/colapso
        document.querySelectorAll('.expand-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const treeItem = this.closest('.tree-item');
                treeItem.classList.toggle('collapsed');
                treeItem.classList.toggle('expanded');
            });
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

    window.editAsset = function(type, id) {
        // Redirecionar para página de edição ou abrir modal de edição
        alert(`Editar ${type} ID: ${id} - Funcionalidade em desenvolvimento`);
    };

    window.deleteAsset = function(type, id) {
        if (confirm(`Tem certeza que deseja excluir este ${type}?`)) {
            // Implementar exclusão
            alert(`Excluir ${type} ID: ${id} - Funcionalidade em desenvolvimento`);
        }
    };

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
                    <p><strong>Filial:</strong> ${asset.filial_tag} - ${asset.filial_descricao}</p>
                    <p><strong>Empresa:</strong> ${asset.empresa}</p>
                    <p><strong>Criado por:</strong> ${asset.usuario_criacao}</p>
                    <p><strong>Data de criação:</strong> ${new Date(asset.data_criacao).toLocaleString('pt-BR')}</p>
                `;
                break;
            case 'equipamento':
                content = `
                    <h3><i class="fas fa-check"></i> ${asset.tag}</h3>
                    <p><strong>Descrição:</strong> ${asset.descricao}</p>
                    <p><strong>Setor:</strong> ${asset.setor_tag} - ${asset.setor_descricao}</p>
                    <p><strong>Filial:</strong> ${asset.filial_tag} - ${asset.filial_descricao}</p>
                    <p><strong>Empresa:</strong> ${asset.empresa}</p>
                    <p><strong>Criado por:</strong> ${asset.usuario_criacao}</p>
                    <p><strong>Data de criação:</strong> ${new Date(asset.data_criacao).toLocaleString('pt-BR')}</p>
                `;
                break;
        }

        // Criar modal simples
        const modal = document.createElement('div');
        modal.className = 'modal-backdrop show';
        modal.innerHTML = `
            <div class="modal" style="max-width: 600px;">
                <div class="modal-header">
                    <h3 class="modal-title">Informações do Ativo</h3>
                    <button class="modal-close" onclick="this.closest('.modal-backdrop').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-backdrop').remove()">Fechar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    // Função para recarregar dados
    window.reloadAssetsData = loadAssetsData;
});

