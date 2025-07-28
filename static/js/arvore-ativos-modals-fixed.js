document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de árvore de ativos carregada');
    
    // Dados dos ativos
    const assetsData = {
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

            console.log('Dados carregados:', {
                filiais: assetsData.filiais.length,
                setores: assetsData.setores.length,
                equipamentos: assetsData.equipamentos.length
            });

            hideLoading();
            renderAssetsTree();

        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            hideLoading();
            showError('Erro ao carregar dados dos ativos. Verifique sua conexão e tente novamente.');
        }
    }

    function showLoading() {
        const container = document.querySelector('.assets-container');
        if (container) {
            container.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>Carregando árvore de ativos...</p>
                </div>
            `;
        }
    }

    function hideLoading() {
        // Loading será substituído pelo conteúdo renderizado
    }

    function showError(message) {
        const container = document.querySelector('.assets-container');
        if (container) {
            container.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <h3>Erro ao Carregar Dados</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="loadAssetsData()">
                        <i class="fas fa-redo"></i> Tentar Novamente
                    </button>
                </div>
            `;
        }
    }

    function renderAssetsTree() {
        const container = document.querySelector('.assets-container');
        if (!container) return;

        if (assetsData.filiais.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📁</div>
                    <h3>Nenhum Ativo Encontrado</h3>
                    <p>Não há filiais cadastradas no sistema.</p>
                </div>
            `;
            return;
        }

        let html = '<div class="assets-tree">';

        assetsData.filiais.forEach(filial => {
            const setoresFilial = assetsData.setores.filter(s => s.filial_id === filial.id);
            
            html += `
                <div class="tree-node filial-node">
                    <div class="node-header" onclick="toggleNode(this)">
                        <i class="fas fa-building node-icon"></i>
                        <span class="node-title">${filial.tag} - ${filial.descricao}</span>
                        <i class="fas fa-chevron-down toggle-icon"></i>
                        <div class="node-actions">
                            <button class="action-btn info-btn" onclick="showFilialInfo(${filial.id})" title="Informações">
                                <i class="fas fa-info-circle"></i>
                            </button>
                        </div>
                    </div>
                    <div class="node-children">
            `;

            setoresFilial.forEach(setor => {
                const equipamentosSetor = assetsData.equipamentos.filter(e => e.setor_id === setor.id);
                
                html += `
                    <div class="tree-node setor-node">
                        <div class="node-header" onclick="toggleNode(this)">
                            <i class="fas fa-layer-group node-icon"></i>
                            <span class="node-title">${setor.tag} - ${setor.descricao}</span>
                            <i class="fas fa-chevron-down toggle-icon"></i>
                            <div class="node-actions">
                                <button class="action-btn info-btn" onclick="showSetorInfo(${setor.id})" title="Informações">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                            </div>
                        </div>
                        <div class="node-children">
                `;

                equipamentosSetor.forEach(equipamento => {
                    html += `
                        <div class="tree-node equipamento-node">
                            <div class="node-header">
                                <i class="fas fa-cog node-icon"></i>
                                <span class="node-title">${equipamento.tag} - ${equipamento.descricao}</span>
                                <div class="node-actions">
                                    <button class="action-btn info-btn" onclick="showEquipamentoInfo(${equipamento.id})" title="Informações">
                                        <i class="fas fa-info-circle"></i>
                                    </button>
                                    <button class="action-btn edit-btn" onclick="editEquipamento(${equipamento.id})" title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });

                html += `
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    // Função para expandir/contrair nós
    window.toggleNode = function(header) {
        const node = header.parentElement;
        const children = node.querySelector('.node-children');
        const icon = header.querySelector('.toggle-icon');
        
        if (children) {
            const isExpanded = children.style.display !== 'none';
            children.style.display = isExpanded ? 'none' : 'block';
            icon.style.transform = isExpanded ? 'rotate(-90deg)' : 'rotate(0deg)';
        }
    };

    // Funções para mostrar informações
    window.showFilialInfo = function(filialId) {
        const filial = assetsData.filiais.find(f => f.id === filialId);
        if (!filial) return;

        const setoresCount = assetsData.setores.filter(s => s.filial_id === filialId).length;
        const equipamentosCount = assetsData.equipamentos.filter(e => {
            const setor = assetsData.setores.find(s => s.id === e.setor_id);
            return setor && setor.filial_id === filialId;
        }).length;

        showInfoModal('Informações da Filial', `
            <div class="info-grid">
                <div class="info-item">
                    <label>Tag:</label>
                    <span>${filial.tag}</span>
                </div>
                <div class="info-item">
                    <label>Descrição:</label>
                    <span>${filial.descricao}</span>
                </div>
                <div class="info-item">
                    <label>Empresa:</label>
                    <span>${filial.empresa}</span>
                </div>
                <div class="info-item">
                    <label>Setores:</label>
                    <span>${setoresCount}</span>
                </div>
                <div class="info-item">
                    <label>Equipamentos:</label>
                    <span>${equipamentosCount}</span>
                </div>
                <div class="info-item">
                    <label>Criado em:</label>
                    <span>${new Date(filial.data_criacao).toLocaleDateString('pt-BR')}</span>
                </div>
                <div class="info-item">
                    <label>Criado por:</label>
                    <span>${filial.usuario_criacao}</span>
                </div>
            </div>
        `);
    };

    window.showSetorInfo = function(setorId) {
        const setor = assetsData.setores.find(s => s.id === setorId);
        if (!setor) return;

        const filial = assetsData.filiais.find(f => f.id === setor.filial_id);
        const equipamentosCount = assetsData.equipamentos.filter(e => e.setor_id === setorId).length;

        showInfoModal('Informações do Setor', `
            <div class="info-grid">
                <div class="info-item">
                    <label>Tag:</label>
                    <span>${setor.tag}</span>
                </div>
                <div class="info-item">
                    <label>Descrição:</label>
                    <span>${setor.descricao}</span>
                </div>
                <div class="info-item">
                    <label>Filial:</label>
                    <span>${filial ? filial.tag + ' - ' + filial.descricao : 'N/A'}</span>
                </div>
                <div class="info-item">
                    <label>Empresa:</label>
                    <span>${setor.empresa}</span>
                </div>
                <div class="info-item">
                    <label>Equipamentos:</label>
                    <span>${equipamentosCount}</span>
                </div>
                <div class="info-item">
                    <label>Criado em:</label>
                    <span>${new Date(setor.data_criacao).toLocaleDateString('pt-BR')}</span>
                </div>
                <div class="info-item">
                    <label>Criado por:</label>
                    <span>${setor.usuario_criacao}</span>
                </div>
            </div>
        `);
    };

    window.showEquipamentoInfo = function(equipamentoId) {
        const equipamento = assetsData.equipamentos.find(e => e.id === equipamentoId);
        if (!equipamento) return;

        const setor = assetsData.setores.find(s => s.id === equipamento.setor_id);
        const filial = setor ? assetsData.filiais.find(f => f.id === setor.filial_id) : null;

        showInfoModal('Informações do Equipamento', `
            <div class="info-grid">
                <div class="info-item">
                    <label>Tag:</label>
                    <span>${equipamento.tag}</span>
                </div>
                <div class="info-item">
                    <label>Descrição:</label>
                    <span>${equipamento.descricao}</span>
                </div>
                <div class="info-item">
                    <label>Setor:</label>
                    <span>${setor ? setor.tag + ' - ' + setor.descricao : 'N/A'}</span>
                </div>
                <div class="info-item">
                    <label>Filial:</label>
                    <span>${filial ? filial.tag + ' - ' + filial.descricao : 'N/A'}</span>
                </div>
                <div class="info-item">
                    <label>Empresa:</label>
                    <span>${equipamento.empresa}</span>
                </div>
                <div class="info-item">
                    <label>Criado em:</label>
                    <span>${new Date(equipamento.data_criacao).toLocaleDateString('pt-BR')}</span>
                </div>
                <div class="info-item">
                    <label>Criado por:</label>
                    <span>${equipamento.usuario_criacao}</span>
                </div>
            </div>
        `);
    };

    window.editEquipamento = function(equipamentoId) {
        const equipamento = assetsData.equipamentos.find(e => e.id === equipamentoId);
        if (!equipamento) return;

        openEditEquipamentoModal(equipamento);
    };

    function showInfoModal(title, content) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        modal.innerHTML = `
            <div class="modal-content" style="
                background: white;
                border-radius: 12px;
                padding: 0;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: scale(0.9);
                transition: transform 0.3s ease;
            ">
                <div class="modal-header" style="
                    padding: 20px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <h2 style="margin: 0; color: #333;">${title}</h2>
                    <button class="close-btn" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Mostrar modal com animação
        setTimeout(() => {
            modal.style.opacity = '1';
            const modalContent = modal.querySelector('.modal-content');
            modalContent.style.transform = 'scale(1)';
        }, 10);

        // Fechar modal
        const closeModal = () => {
            modal.style.opacity = '0';
            const modalContent = modal.querySelector('.modal-content');
            modalContent.style.transform = 'scale(0.9)';
            setTimeout(() => {
                if (document.body.contains(modal)) {
                    document.body.removeChild(modal);
                }
            }, 300);
        };

        modal.querySelector('.close-btn').addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    function openEditEquipamentoModal(equipamento) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        modal.innerHTML = `
            <div class="modal-content" style="
                background: white;
                border-radius: 12px;
                padding: 0;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: scale(0.9);
                transition: transform 0.3s ease;
            ">
                <div class="modal-header" style="
                    padding: 20px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <h2 style="margin: 0; color: #333;">Editar Equipamento</h2>
                    <button class="close-btn" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <form id="edit-equipamento-form">
                        <div class="form-group" style="margin-bottom: 15px;">
                            <label for="tag" style="display: block; margin-bottom: 5px; font-weight: 600;">Tag</label>
                            <input type="text" id="tag" name="tag" value="${equipamento.tag}" required style="
                                width: 100%;
                                padding: 10px;
                                border: 1px solid #ddd;
                                border-radius: 6px;
                                font-size: 14px;
                                box-sizing: border-box;
                            ">
                        </div>
                        <div class="form-group" style="margin-bottom: 15px;">
                            <label for="descricao" style="display: block; margin-bottom: 5px; font-weight: 600;">Descrição</label>
                            <input type="text" id="descricao" name="descricao" value="${equipamento.descricao}" required style="
                                width: 100%;
                                padding: 10px;
                                border: 1px solid #ddd;
                                border-radius: 6px;
                                font-size: 14px;
                                box-sizing: border-box;
                            ">
                        </div>
                        <div class="form-group" style="margin-bottom: 20px;">
                            <label for="setor_id" style="display: block; margin-bottom: 5px; font-weight: 600;">Setor</label>
                            <select id="setor_id" name="setor_id" required style="
                                width: 100%;
                                padding: 10px;
                                border: 1px solid #ddd;
                                border-radius: 6px;
                                font-size: 14px;
                                box-sizing: border-box;
                            ">
                                ${assetsData.setores.map(s => `<option value="${s.id}" ${s.id === equipamento.setor_id ? 'selected' : ''}>${s.tag} - ${s.descricao}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-actions" style="
                            display: flex;
                            gap: 10px;
                            justify-content: flex-end;
                        ">
                            <button type="button" class="btn btn-secondary close-modal" style="
                                padding: 10px 20px;
                                border: 1px solid #ddd;
                                background: white;
                                color: #666;
                                border-radius: 6px;
                                cursor: pointer;
                            ">Cancelar</button>
                            <button type="submit" class="btn btn-primary" style="
                                padding: 10px 20px;
                                border: none;
                                background: #9956a8;
                                color: white;
                                border-radius: 6px;
                                cursor: pointer;
                            ">Salvar Alterações</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Mostrar modal com animação
        setTimeout(() => {
            modal.style.opacity = '1';
            const modalContent = modal.querySelector('.modal-content');
            modalContent.style.transform = 'scale(1)';
        }, 10);

        // Fechar modal
        const closeModal = () => {
            modal.style.opacity = '0';
            const modalContent = modal.querySelector('.modal-content');
            modalContent.style.transform = 'scale(0.9)';
            setTimeout(() => {
                if (document.body.contains(modal)) {
                    document.body.removeChild(modal);
                }
            }, 300);
        };

        modal.querySelector('.close-btn').addEventListener('click', closeModal);
        modal.querySelector('.close-modal').addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Submeter formulário
        modal.querySelector('#edit-equipamento-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                tag: modal.querySelector('#tag').value,
                descricao: modal.querySelector('#descricao').value,
                setor_id: parseInt(modal.querySelector('#setor_id').value)
            };
            
            try {
                const response = await fetch(`/api/equipamentos/${equipamento.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        // Atualizar dados locais
                        const index = assetsData.equipamentos.findIndex(e => e.id === equipamento.id);
                        if (index !== -1) {
                            assetsData.equipamentos[index] = { ...assetsData.equipamentos[index], ...formData };
                        }
                        
                        closeModal();
                        renderAssetsTree();
                        showNotification('Equipamento atualizado com sucesso!', 'success');
                    } else {
                        throw new Error(result.message || 'Erro ao atualizar equipamento');
                    }
                } else {
                    throw new Error('Erro na requisição');
                }
            } catch (error) {
                console.error('Erro ao atualizar equipamento:', error);
                showNotification('Erro ao atualizar equipamento: ' + error.message, 'error');
            }
        });
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10001;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            max-width: 300px;
        `;
        
        switch (type) {
            case 'success':
                notification.style.background = '#4caf50';
                break;
            case 'error':
                notification.style.background = '#f44336';
                break;
            case 'warning':
                notification.style.background = '#ff9800';
                break;
            default:
                notification.style.background = '#2196f3';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
});

