// Dados globais
let equipamentosData = [];
let filiaisData = [];
let setoresData = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Iniciando página de Manutenção Preventiva');
    carregarDados();
});

// Carregar dados iniciais
async function carregarDados() {
    try {
        console.log('📡 Carregando dados das APIs...');
        
        // Carregar filiais
        const filiaisResponse = await fetch('/api/filiais');
        if (filiaisResponse.ok) {
            const filiaisResult = await filiaisResponse.json();
            filiaisData = filiaisResult.filiais || [];
            console.log(`🏢 ${filiaisData.length} filiais carregadas`);
            popularFiliais();
        }
        
        // Carregar todos os equipamentos
        const equipamentosResponse = await fetch('/api/equipamentos');
        if (equipamentosResponse.ok) {
            const equipamentosResult = await equipamentosResponse.json();
            equipamentosData = equipamentosResult.equipamentos || [];
            console.log(`⚙️ ${equipamentosData.length} equipamentos carregados`);
            renderizarEquipamentos(equipamentosData);
        }
        
        // Carregar todos os setores
        const setoresResponse = await fetch('/api/setores');
        if (setoresResponse.ok) {
            const setoresResult = await setoresResponse.json();
            setoresData = setoresResult.setores || [];
            console.log(`🏭 ${setoresData.length} setores carregados`);
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        mostrarErro('Erro ao carregar dados. Tente novamente.');
    }
}

// Popular select de filiais
function popularFiliais() {
    const filialSelect = document.getElementById('filial-filter');
    filialSelect.innerHTML = '<option value="">Todas as filiais</option>';
    
    filiaisData.forEach(filial => {
        const option = document.createElement('option');
        option.value = filial.id;
        option.textContent = `${filial.tag} - ${filial.descricao}`;
        filialSelect.appendChild(option);
    });
    
    console.log('🏢 Select de filiais populado');
}

// Carregar setores baseado na filial selecionada
async function carregarSetores() {
    const filialId = document.getElementById('filial-filter').value;
    const setorSelect = document.getElementById('setor-filter');
    
    console.log(`🔄 Carregando setores para filial: ${filialId || 'todas'}`);
    
    setorSelect.innerHTML = '<option value="">Todos os setores</option>';
    
    try {
        let setoresFiltrados = [];
        
        if (filialId) {
            // Filtrar setores pela filial selecionada
            setoresFiltrados = setoresData.filter(setor => setor.filial_id == filialId);
        } else {
            // Mostrar todos os setores
            setoresFiltrados = setoresData;
        }
        
        setoresFiltrados.forEach(setor => {
            const option = document.createElement('option');
            option.value = setor.id;
            option.textContent = `${setor.tag} - ${setor.descricao}`;
            setorSelect.appendChild(option);
        });
        
        console.log(`🏭 ${setoresFiltrados.length} setores carregados para a filial`);
        
        // Recarregar equipamentos com o novo filtro
        carregarEquipamentos();
        
    } catch (error) {
        console.error('❌ Erro ao carregar setores:', error);
    }
}

// Carregar equipamentos baseado nos filtros
async function carregarEquipamentos() {
    const filialId = document.getElementById('filial-filter').value;
    const setorId = document.getElementById('setor-filter').value;
    
    console.log(`🔄 Filtrando equipamentos - Filial: ${filialId || 'todas'}, Setor: ${setorId || 'todos'}`);
    
    try {
        let equipamentosFiltrados = equipamentosData;
        
        // Filtrar por setor se selecionado
        if (setorId) {
            equipamentosFiltrados = equipamentosFiltrados.filter(eq => eq.setor_id == setorId);
        }
        // Se não há setor específico mas há filial, filtrar por filial
        else if (filialId) {
            // Primeiro, encontrar todos os setores da filial
            const setoresDaFilial = setoresData.filter(setor => setor.filial_id == filialId);
            const setorIds = setoresDaFilial.map(setor => setor.id);
            
            // Filtrar equipamentos que pertencem aos setores da filial
            equipamentosFiltrados = equipamentosFiltrados.filter(eq => setorIds.includes(eq.setor_id));
        }
        
        console.log(`⚙️ ${equipamentosFiltrados.length} equipamentos após filtro`);
        renderizarEquipamentos(equipamentosFiltrados);
        
    } catch (error) {
        console.error('❌ Erro ao filtrar equipamentos:', error);
    }
}

// Filtrar equipamentos por status
function filtrarEquipamentos() {
    const statusFilter = document.getElementById('status-filter').value;
    const filialId = document.getElementById('filial-filter').value;
    const setorId = document.getElementById('setor-filter').value;
    
    console.log(`🔄 Aplicando filtro de status: ${statusFilter || 'todos'}`);
    
    let equipamentosFiltrados = equipamentosData;
    
    // Aplicar filtros de localização primeiro
    if (setorId) {
        equipamentosFiltrados = equipamentosFiltrados.filter(eq => eq.setor_id == setorId);
    } else if (filialId) {
        const setoresDaFilial = setoresData.filter(setor => setor.filial_id == filialId);
        const setorIds = setoresDaFilial.map(setor => setor.id);
        equipamentosFiltrados = equipamentosFiltrados.filter(eq => setorIds.includes(eq.setor_id));
    }
    
    // Aplicar filtro de status
    if (statusFilter) {
        equipamentosFiltrados = equipamentosFiltrados.filter(eq => {
            // Simular status baseado no ID (para demonstração)
            const equipId = eq.id;
            if (statusFilter === 'active') return equipId % 3 !== 0;
            if (statusFilter === 'inactive') return equipId % 5 === 0;
            if (statusFilter === 'maintenance') return equipId % 7 === 0;
            return true;
        });
    }
    
    console.log(`⚙️ ${equipamentosFiltrados.length} equipamentos após filtro de status`);
    renderizarEquipamentos(equipamentosFiltrados);
}

// Renderizar equipamentos como cards
function renderizarEquipamentos(equipamentos) {
    const container = document.getElementById('equipment-container');
    
    if (equipamentos.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>Nenhum equipamento encontrado</h3>
                <p>Tente ajustar os filtros para encontrar equipamentos.</p>
            </div>
        `;
        return;
    }
    
    const grid = document.createElement('div');
    grid.className = 'equipment-grid';
    
    equipamentos.forEach(equipamento => {
        const card = criarCardEquipamento(equipamento);
        grid.appendChild(card);
    });
    
    container.innerHTML = '';
    container.appendChild(grid);
    
    console.log(`🎨 ${equipamentos.length} cards de equipamentos renderizados`);
}

// Criar card individual do equipamento
function criarCardEquipamento(equipamento) {
    const card = document.createElement('div');
    card.className = 'equipment-card';
    
    // Determinar status baseado no ID (simulação)
    const equipId = equipamento.id;
    let status = 'active';
    let statusClass = 'active';
    
    if (equipId % 5 === 0) {
        status = 'inactive';
        statusClass = 'inactive';
    } else if (equipId % 7 === 0) {
        status = 'maintenance';
        statusClass = 'maintenance';
    }
    
    // Encontrar informações do setor
    const setor = setoresData.find(s => s.id === equipamento.setor_id);
    const setorInfo = setor ? `${setor.tag} - ${setor.descricao}` : 'Setor não encontrado';
    
    card.innerHTML = `
        <div class="equipment-image">
            <div class="status-indicator ${statusClass}"></div>
            <div class="placeholder-icon">
                <i class="fas fa-cogs"></i>
            </div>
        </div>
        
        <div class="equipment-info">
            <div class="equipment-code">${equipamento.tag}</div>
            <div class="equipment-name">${equipamento.descricao}</div>
            <div class="equipment-details">
                ${setorInfo}<br>
                Criado por: ${equipamento.usuario_criacao || 'Sistema'}
            </div>
            
            <div class="equipment-actions">
                <button class="action-btn technical" onclick="abrirDadosTecnicos(${equipamento.id})">
                    <i class="fas fa-chart-bar"></i>
                    <div class="tooltip">Dados Técnicos</div>
                </button>
                
                <button class="action-btn maintenance" onclick="abrirPlanoManutencao(${equipamento.id})">
                    <i class="fas fa-tools"></i>
                    <div class="tooltip">Plano de Manutenção</div>
                </button>
                
                <button class="action-btn transfer" onclick="abrirTransferencia(${equipamento.id})">
                    <i class="fas fa-exchange-alt"></i>
                    <div class="tooltip">Transferência</div>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Ações dos botões
function abrirDadosTecnicos(equipamentoId) {
    console.log(`📊 Abrindo dados técnicos do equipamento ${equipamentoId}`);
    
    const equipamento = equipamentosData.find(eq => eq.id === equipamentoId);
    if (!equipamento) {
        alert('Equipamento não encontrado!');
        return;
    }
    
    // Criar modal de dados técnicos
    const modal = criarModal('Dados Técnicos', `
        <div style="padding: 20px;">
            <h3 style="margin-top: 0; color: #333;">${equipamento.tag}</h3>
            <p><strong>Descrição:</strong> ${equipamento.descricao}</p>
            <p><strong>ID:</strong> ${equipamento.id}</p>
            <p><strong>Setor:</strong> ${getSetorNome(equipamento.setor_id)}</p>
            <p><strong>Criado por:</strong> ${equipamento.usuario_criacao || 'Sistema'}</p>
            <p><strong>Data de criação:</strong> ${formatarData(equipamento.data_criacao)}</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <h4 style="color: #666; margin-bottom: 15px;">Especificações Técnicas</h4>
                <p><em>Dados técnicos detalhados serão implementados aqui...</em></p>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
}

function abrirPlanoManutencao(equipamentoId) {
    console.log(`🔧 Abrindo plano de manutenção do equipamento ${equipamentoId}`);
    
    const equipamento = equipamentosData.find(eq => eq.id === equipamentoId);
    if (!equipamento) {
        alert('Equipamento não encontrado!');
        return;
    }
    
    // Criar modal de plano de manutenção
    const modal = criarModal('Plano de Manutenção', `
        <div style="padding: 20px;">
            <h3 style="margin-top: 0; color: #333;">${equipamento.tag}</h3>
            <p style="color: #666; margin-bottom: 30px;">${equipamento.descricao}</p>
            
            <div style="margin-bottom: 25px;">
                <h4 style="color: #9956a8; margin-bottom: 15px;">Configurar Manutenção Preventiva</h4>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Frequência:</label>
                    <select style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                        <option>Semanal</option>
                        <option>Quinzenal</option>
                        <option>Mensal</option>
                        <option>Trimestral</option>
                        <option>Semestral</option>
                        <option>Anual</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Próxima manutenção:</label>
                    <input type="date" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Observações:</label>
                    <textarea rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; resize: vertical;" placeholder="Instruções específicas para a manutenção..."></textarea>
                </div>
                
                <button onclick="salvarPlanoManutencao(${equipamentoId})" style="
                    background: #9956a8;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                ">Salvar Plano</button>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
}

function abrirTransferencia(equipamentoId) {
    console.log(`🔄 Abrindo transferência do equipamento ${equipamentoId}`);
    
    const equipamento = equipamentosData.find(eq => eq.id === equipamentoId);
    if (!equipamento) {
        alert('Equipamento não encontrado!');
        return;
    }
    
    // Criar modal de transferência
    const modal = criarModal('Transferência de Equipamento', `
        <div style="padding: 20px;">
            <h3 style="margin-top: 0; color: #333;">${equipamento.tag}</h3>
            <p style="color: #666; margin-bottom: 30px;">${equipamento.descricao}</p>
            
            <div style="margin-bottom: 25px;">
                <h4 style="color: #28a745; margin-bottom: 15px;">Transferir para:</h4>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Nova Filial:</label>
                    <select id="transfer-filial" onchange="carregarSetoresTransferencia()" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                        <option value="">Selecione uma filial</option>
                        ${filiaisData.map(filial => `<option value="${filial.id}">${filial.tag} - ${filial.descricao}</option>`).join('')}
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Novo Setor:</label>
                    <select id="transfer-setor" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                        <option value="">Primeiro selecione uma filial</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Motivo da transferência:</label>
                    <textarea rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; resize: vertical;" placeholder="Descreva o motivo da transferência..."></textarea>
                </div>
                
                <button onclick="executarTransferencia(${equipamentoId})" style="
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                ">Confirmar Transferência</button>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
}

// Funções auxiliares para os modais
function carregarSetoresTransferencia() {
    const filialId = document.getElementById('transfer-filial').value;
    const setorSelect = document.getElementById('transfer-setor');
    
    setorSelect.innerHTML = '<option value="">Selecione um setor</option>';
    
    if (filialId) {
        const setoresDaFilial = setoresData.filter(setor => setor.filial_id == filialId);
        setoresDaFilial.forEach(setor => {
            const option = document.createElement('option');
            option.value = setor.id;
            option.textContent = `${setor.tag} - ${setor.descricao}`;
            setorSelect.appendChild(option);
        });
    }
}

function salvarPlanoManutencao(equipamentoId) {
    console.log(`💾 Salvando plano de manutenção para equipamento ${equipamentoId}`);
    alert('Plano de manutenção salvo com sucesso!\n\n(Esta é uma simulação - a funcionalidade completa será implementada)');
    fecharModal();
}

function executarTransferencia(equipamentoId) {
    const filialId = document.getElementById('transfer-filial').value;
    const setorId = document.getElementById('transfer-setor').value;
    
    if (!filialId || !setorId) {
        alert('Por favor, selecione a filial e o setor de destino.');
        return;
    }
    
    console.log(`🔄 Executando transferência do equipamento ${equipamentoId} para setor ${setorId}`);
    alert('Transferência realizada com sucesso!\n\n(Esta é uma simulação - a funcionalidade completa será implementada)');
    fecharModal();
}

// Função para criar modal genérico
function criarModal(titulo, conteudo) {
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
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        ">
            <div style="
                padding: 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <h2 style="margin: 0; color: #333;">${titulo}</h2>
                <button onclick="fecharModal()" style="
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
            ${conteudo}
        </div>
    `;
    
    // Mostrar modal com animação
    setTimeout(() => {
        modal.style.opacity = '1';
        const modalContent = modal.querySelector('.modal-content');
        modalContent.style.transform = 'scale(1)';
    }, 10);
    
    // Fechar ao clicar no fundo
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            fecharModal();
        }
    });
    
    return modal;
}

function fecharModal() {
    const modals = document.querySelectorAll('[style*="position: fixed"][style*="z-index: 10000"]');
    modals.forEach(modal => {
        modal.style.opacity = '0';
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.9)';
        }
        setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        }, 300);
    });
}

// Funções utilitárias
function getSetorNome(setorId) {
    const setor = setoresData.find(s => s.id === setorId);
    return setor ? `${setor.tag} - ${setor.descricao}` : 'Setor não encontrado';
}

function formatarData(dataString) {
    if (!dataString) return 'Data não disponível';
    
    try {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Data inválida';
    }
}

function mostrarErro(mensagem) {
    const container = document.getElementById('equipment-container');
    container.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: #dc3545;">
            <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 20px;"></i>
            <h3>Erro</h3>
            <p>${mensagem}</p>
            <button onclick="carregarDados()" style="
                background: #9956a8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                margin-top: 15px;
            ">Tentar Novamente</button>
        </div>
    `;
}

