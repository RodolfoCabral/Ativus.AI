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
        document.querySelectorAll('.tree-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
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

    window.editAsset = async function(type, id) {
        try {
            // Verificar permissões (apenas admin e master podem editar)
            const userProfile = await getCurrentUserProfile();
            if (!userProfile || (userProfile !== 'admin' && userProfile !== 'master')) {
                alert('Apenas administradores podem editar ativos.');
                return;
            }
            
            // Buscar dados do ativo
            const response = await fetch(`/api/${type}s/${id}`);
            const data = await response.json();
            
            if (!data.success) {
                alert('Erro ao carregar dados: ' + data.message);
                return;
            }
            
            // Abrir modal de edição baseado no tipo
            switch(type) {
                case 'filial':
                    openEditFilialModal(data.filial);
                    break;
                case 'setor':
                    openEditSetorModal(data.setor);
                    break;
                case 'equipamento':
                    openEditEquipamentoModal(data.equipamento);
                    break;
            }
            
        } catch (error) {
            console.error('Erro ao editar ativo:', error);
            alert('Erro ao carregar dados para edição.');
        }
    };

    window.deleteAsset = async function(type, id) {
        try {
            // Verificar permissões (apenas admin e master podem excluir)
            const userProfile = await getCurrentUserProfile();
            if (!userProfile || (userProfile !== 'admin' && userProfile !== 'master')) {
                alert('Apenas administradores podem excluir ativos.');
                return;
            }
            
            // Buscar dados do ativo para mostrar informações na confirmação
            const response = await fetch(`/api/${type}s/${id}`);
            const data = await response.json();
            
            if (!data.success) {
                alert('Erro ao carregar dados: ' + data.message);
                return;
            }
            
            const asset = data[type];
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
            
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // Confirmação adicional para filiais e setores
            if (type === 'filial' || type === 'setor') {
                if (!confirm(`Confirma novamente? Esta ação removerá TODOS os dados relacionados!`)) {
                    return;
                }
            }
            
            // Executar exclusão
            const deleteResponse = await fetch(`/api/${type}s/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const deleteData = await deleteResponse.json();
            
            if (deleteData.success) {
                alert(deleteData.message);
                // Recarregar dados da árvore
                loadAssetsData();
            } else {
                alert('Erro ao excluir: ' + deleteData.message);
            }
            
        } catch (error) {
            console.error('Erro ao excluir ativo:', error);
            alert('Erro ao excluir ativo.');
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


    // ==================== FUNÇÕES AUXILIARES ====================
    
    let currentUserProfile = '';
    let currentUserCompany = '';
    
    async function getCurrentUserProfile() {
        if (currentUserProfile) {
            return currentUserProfile;
        }
        
        try {
            const response = await fetch('/api/user');
            const data = await response.json();
            
            if (data.success && data.user) {
                currentUserProfile = data.user.profile;
                currentUserCompany = data.user.company;
                return currentUserProfile;
            }
        } catch (error) {
            console.error('Erro ao obter perfil do usuário:', error);
        }
        
        return 'user'; // Fallback
    }
    
    // ==================== MODAIS DE EDIÇÃO ====================
    
    function openEditFilialModal(filial) {
        // Criar modal de edição para filial
        const modalHtml = `
            <div id="edit-filial-modal" class="modal-backdrop">
                <div class="modal" style="max-width: 800px;">
                    <div class="modal-header">
                        <h3 class="modal-title">Editar Filial</h3>
                        <button class="modal-close" onclick="closeEditFilialModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="edit-filial-form">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit-filial-tag">Tag da Filial *</label>
                                    <input type="text" id="edit-filial-tag" name="tag" value="${filial.tag}" required>
                                </div>
                                <div class="form-group">
                                    <label for="edit-filial-descricao">Descrição *</label>
                                    <input type="text" id="edit-filial-descricao" name="descricao" value="${filial.descricao}" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="edit-filial-endereco">Endereço *</label>
                                <input type="text" id="edit-filial-endereco" name="endereco" value="${filial.endereco}" required>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit-filial-cidade">Cidade *</label>
                                    <input type="text" id="edit-filial-cidade" name="cidade" value="${filial.cidade}" required>
                                </div>
                                <div class="form-group">
                                    <label for="edit-filial-estado">Estado *</label>
                                    <select id="edit-filial-estado" name="estado" required>
                                        <option value="">Selecione...</option>
                                        <option value="AC" ${filial.estado === 'AC' ? 'selected' : ''}>Acre</option>
                                        <option value="AL" ${filial.estado === 'AL' ? 'selected' : ''}>Alagoas</option>
                                        <option value="AP" ${filial.estado === 'AP' ? 'selected' : ''}>Amapá</option>
                                        <option value="AM" ${filial.estado === 'AM' ? 'selected' : ''}>Amazonas</option>
                                        <option value="BA" ${filial.estado === 'BA' ? 'selected' : ''}>Bahia</option>
                                        <option value="CE" ${filial.estado === 'CE' ? 'selected' : ''}>Ceará</option>
                                        <option value="DF" ${filial.estado === 'DF' ? 'selected' : ''}>Distrito Federal</option>
                                        <option value="ES" ${filial.estado === 'ES' ? 'selected' : ''}>Espírito Santo</option>
                                        <option value="GO" ${filial.estado === 'GO' ? 'selected' : ''}>Goiás</option>
                                        <option value="MA" ${filial.estado === 'MA' ? 'selected' : ''}>Maranhão</option>
                                        <option value="MT" ${filial.estado === 'MT' ? 'selected' : ''}>Mato Grosso</option>
                                        <option value="MS" ${filial.estado === 'MS' ? 'selected' : ''}>Mato Grosso do Sul</option>
                                        <option value="MG" ${filial.estado === 'MG' ? 'selected' : ''}>Minas Gerais</option>
                                        <option value="PA" ${filial.estado === 'PA' ? 'selected' : ''}>Pará</option>
                                        <option value="PB" ${filial.estado === 'PB' ? 'selected' : ''}>Paraíba</option>
                                        <option value="PR" ${filial.estado === 'PR' ? 'selected' : ''}>Paraná</option>
                                        <option value="PE" ${filial.estado === 'PE' ? 'selected' : ''}>Pernambuco</option>
                                        <option value="PI" ${filial.estado === 'PI' ? 'selected' : ''}>Piauí</option>
                                        <option value="RJ" ${filial.estado === 'RJ' ? 'selected' : ''}>Rio de Janeiro</option>
                                        <option value="RN" ${filial.estado === 'RN' ? 'selected' : ''}>Rio Grande do Norte</option>
                                        <option value="RS" ${filial.estado === 'RS' ? 'selected' : ''}>Rio Grande do Sul</option>
                                        <option value="RO" ${filial.estado === 'RO' ? 'selected' : ''}>Rondônia</option>
                                        <option value="RR" ${filial.estado === 'RR' ? 'selected' : ''}>Roraima</option>
                                        <option value="SC" ${filial.estado === 'SC' ? 'selected' : ''}>Santa Catarina</option>
                                        <option value="SP" ${filial.estado === 'SP' ? 'selected' : ''}>São Paulo</option>
                                        <option value="SE" ${filial.estado === 'SE' ? 'selected' : ''}>Sergipe</option>
                                        <option value="TO" ${filial.estado === 'TO' ? 'selected' : ''}>Tocantins</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit-filial-email">E-mail *</label>
                                    <input type="email" id="edit-filial-email" name="email" value="${filial.email}" required>
                                </div>
                                <div class="form-group">
                                    <label for="edit-filial-telefone">Telefone *</label>
                                    <input type="tel" id="edit-filial-telefone" name="telefone" value="${filial.telefone}" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="edit-filial-cnpj">CNPJ *</label>
                                <input type="text" id="edit-filial-cnpj" name="cnpj" value="${filial.cnpj}" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeEditFilialModal()">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="saveEditFilial(${filial.id})">Salvar Alterações</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        document.getElementById('edit-filial-modal').style.display = 'flex';
    }
    
    function openEditSetorModal(setor) {
        // Primeiro, carregar lista de filiais
        fetch('/api/filiais')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const filiaisOptions = data.filiais.map(filial => 
                        `<option value="${filial.id}" ${filial.id === setor.filial_id ? 'selected' : ''}>${filial.tag} - ${filial.descricao}</option>`
                    ).join('');
                    
                    const modalHtml = `
                        <div id="edit-setor-modal" class="modal-backdrop">
                            <div class="modal" style="max-width: 600px;">
                                <div class="modal-header">
                                    <h3 class="modal-title">Editar Setor</h3>
                                    <button class="modal-close" onclick="closeEditSetorModal()">&times;</button>
                                </div>
                                <div class="modal-body">
                                    <form id="edit-setor-form">
                                        <div class="form-group">
                                            <label for="edit-setor-filial">Filial *</label>
                                            <select id="edit-setor-filial" name="filial_id" required>
                                                <option value="">Selecione uma filial...</option>
                                                ${filiaisOptions}
                                            </select>
                                        </div>
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label for="edit-setor-tag">Tag do Setor *</label>
                                                <input type="text" id="edit-setor-tag" name="tag" value="${setor.tag}" required>
                                            </div>
                                            <div class="form-group">
                                                <label for="edit-setor-descricao">Descrição *</label>
                                                <input type="text" id="edit-setor-descricao" name="descricao" value="${setor.descricao}" required>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" onclick="closeEditSetorModal()">Cancelar</button>
                                    <button type="button" class="btn btn-primary" onclick="saveEditSetor(${setor.id})">Salvar Alterações</button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    document.getElementById('edit-setor-modal').style.display = 'flex';
                }
            });
    }
    
    function openEditEquipamentoModal(equipamento) {
        // Primeiro, carregar lista de setores
        fetch('/api/setores')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const setoresOptions = data.setores.map(setor => 
                        `<option value="${setor.id}" ${setor.id === equipamento.setor_id ? 'selected' : ''}>${setor.filial_tag} > ${setor.tag} - ${setor.descricao}</option>`
                    ).join('');
                    
                    const modalHtml = `
                        <div id="edit-equipamento-modal" class="modal-backdrop">
                            <div class="modal" style="max-width: 600px;">
                                <div class="modal-header">
                                    <h3 class="modal-title">Editar Equipamento</h3>
                                    <button class="modal-close" onclick="closeEditEquipamentoModal()">&times;</button>
                                </div>
                                <div class="modal-body">
                                    <form id="edit-equipamento-form">
                                        <div class="form-group">
                                            <label for="edit-equipamento-setor">Setor *</label>
                                            <select id="edit-equipamento-setor" name="setor_id" required>
                                                <option value="">Selecione um setor...</option>
                                                ${setoresOptions}
                                            </select>
                                        </div>
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label for="edit-equipamento-tag">Tag do Equipamento *</label>
                                                <input type="text" id="edit-equipamento-tag" name="tag" value="${equipamento.tag}" required>
                                            </div>
                                            <div class="form-group">
                                                <label for="edit-equipamento-descricao">Descrição *</label>
                                                <input type="text" id="edit-equipamento-descricao" name="descricao" value="${equipamento.descricao}" required>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" onclick="closeEditEquipamentoModal()">Cancelar</button>
                                    <button type="button" class="btn btn-primary" onclick="saveEditEquipamento(${equipamento.id})">Salvar Alterações</button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    document.getElementById('edit-equipamento-modal').style.display = 'flex';
                }
            });
    }
    
    // ==================== FUNÇÕES DE FECHAMENTO DE MODAIS ====================
    
    window.closeEditFilialModal = function() {
        const modal = document.getElementById('edit-filial-modal');
        if (modal) {
            modal.remove();
        }
    };
    
    window.closeEditSetorModal = function() {
        const modal = document.getElementById('edit-setor-modal');
        if (modal) {
            modal.remove();
        }
    };
    
    window.closeEditEquipamentoModal = function() {
        const modal = document.getElementById('edit-equipamento-modal');
        if (modal) {
            modal.remove();
        }
    };
    
    // ==================== FUNÇÕES DE SALVAMENTO ====================
    
    window.saveEditFilial = async function(filialId) {
        try {
            const form = document.getElementById('edit-filial-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(`/api/filiais/${filialId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Filial atualizada com sucesso!');
                closeEditFilialModal();
                loadAssetsData(); // Recarregar dados
            } else {
                alert('Erro ao atualizar filial: ' + result.message);
            }
            
        } catch (error) {
            console.error('Erro ao salvar filial:', error);
            alert('Erro ao salvar alterações.');
        }
    };
    
    window.saveEditSetor = async function(setorId) {
        try {
            const form = document.getElementById('edit-setor-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(`/api/setores/${setorId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Setor atualizado com sucesso!');
                closeEditSetorModal();
                loadAssetsData(); // Recarregar dados
            } else {
                alert('Erro ao atualizar setor: ' + result.message);
            }
            
        } catch (error) {
            console.error('Erro ao salvar setor:', error);
            alert('Erro ao salvar alterações.');
        }
    };
    
    window.saveEditEquipamento = async function(equipamentoId) {
        try {
            const form = document.getElementById('edit-equipamento-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(`/api/equipamentos/${equipamentoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Equipamento atualizado com sucesso!');
                closeEditEquipamentoModal();
                loadAssetsData(); // Recarregar dados
            } else {
                alert('Erro ao atualizar equipamento: ' + result.message);
            }
            
        } catch (error) {
            console.error('Erro ao salvar equipamento:', error);
            alert('Erro ao salvar alterações.');
        }
    };

