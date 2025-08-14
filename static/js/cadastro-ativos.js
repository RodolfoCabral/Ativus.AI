document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.toggle('show');
                }
            } else {
                dashboardContainer.classList.toggle('sidebar-collapsed');
            }
        });
    }
    
    // Fechar sidebar em mobile quando clicar no overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('show');
        });
    }
    
    // User dropdown
    const userDropdownBtn = document.querySelector('.user-dropdown-btn');
    const userDropdownContent = document.querySelector('.user-dropdown-content');
    
    if (userDropdownBtn && userDropdownContent) {
        userDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            userDropdownContent.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.user-dropdown')) {
                if (userDropdownContent.classList.contains('show')) {
                    userDropdownContent.classList.remove('show');
                }
            }
        });
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            fetch('/api/logout')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/';
                    } else {
                        alert('Erro ao fazer logout. Tente novamente.');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro de conexão. Tente novamente mais tarde.');
                });
        });
    }
});

// Funções para navegação
function navigateTo(url) {
    window.location.href = url;
}

// Funções para modal de cadastro
function showCadastroOptions() {
    const modal = document.getElementById('cadastro-modal');
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function closeCadastroModal() {
    const modal = document.getElementById('cadastro-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    // Fechar todos os formulários
    closeAllForms();
}

function closeAllForms() {
    const forms = ['filial-form-modal', 'setor-form-modal', 'equipamento-form-modal'];
    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.style.display = 'none';
        }
    });
}

// Funções para abrir formulários específicos
function openFilialForm() {
    closeCadastroModal();
    const modal = document.getElementById('filial-form-modal');
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function openSetorForm() {
    closeCadastroModal();
    loadFiliais(); // Carregar filiais para o select
    const modal = document.getElementById('setor-form-modal');
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function openEquipamentoForm() {
    closeCadastroModal();
    loadSetores(); // Carregar setores para o select
    const modal = document.getElementById('equipamento-form-modal');
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

// Funções para fechar formulários específicos
function closeFilialForm() {
    const modal = document.getElementById('filial-form-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    document.getElementById('filial-form').reset();
}

function closeSetorForm() {
    const modal = document.getElementById('setor-form-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    document.getElementById('setor-form').reset();
}

function closeEquipamentoForm() {
    const modal = document.getElementById('equipamento-form-modal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
    document.getElementById('equipamento-form').reset();
}

// Funções para carregar dados
function loadFiliais() {
    fetch('/api/filiais')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('setor-filial-select');
                select.innerHTML = '<option value="">Selecione uma filial</option>';
                
                data.filiais.forEach(filial => {
                    const option = document.createElement('option');
                    option.value = filial.id;
                    option.textContent = `${filial.tag} - ${filial.descricao}`;
                    select.appendChild(option);
                });
            } else {
                showMessage('Erro ao carregar filiais: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro ao carregar filiais', 'error');
        });
}

function loadSetores() {
    fetch('/api/setores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('equipamento-setor-select');
                select.innerHTML = '<option value="">Selecione um setor</option>';
                
                data.setores.forEach(setor => {
                    const option = document.createElement('option');
                    option.value = setor.id;
                    option.textContent = `${setor.tag} - ${setor.descricao} (${setor.filial_tag})`;
                    select.appendChild(option);
                });
            } else {
                showMessage('Erro ao carregar setores: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showMessage('Erro ao carregar setores', 'error');
        });
}

// Funções para salvar dados
function saveFilial() {
    const form = document.getElementById('filial-form');
    const formData = new FormData(form);
    
    const data = {
        tag: formData.get('tag'),
        descricao: formData.get('descricao'),
        endereco: formData.get('endereco'),
        cidade: formData.get('cidade'),
        estado: formData.get('estado'),
        email: formData.get('email'),
        telefone: formData.get('telefone'),
        cnpj: formData.get('cnpj')
    };
    
    // Validar campos obrigatórios
    const requiredFields = ['tag', 'descricao', 'endereco', 'cidade', 'estado', 'email', 'telefone', 'cnpj'];
    for (let field of requiredFields) {
        if (!data[field]) {
            showMessage(`Campo ${field} é obrigatório`, 'error');
            return;
        }
    }
    
    fetch('/api/filiais', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Filial cadastrada com sucesso!', 'success');
            closeFilialForm();
        } else {
            showMessage('Erro ao cadastrar filial: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showMessage('Erro ao cadastrar filial', 'error');
    });
}

function saveSetor() {
    const form = document.getElementById('setor-form');
    const formData = new FormData(form);
    
    const data = {
        tag: formData.get('tag'),
        descricao: formData.get('descricao'),
        filial_id: parseInt(formData.get('filial_id'))
    };
    
    // Validar campos obrigatórios
    if (!data.tag || !data.descricao || !data.filial_id) {
        showMessage('Todos os campos são obrigatórios', 'error');
        return;
    }
    
    fetch('/api/setores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Setor cadastrado com sucesso!', 'success');
            closeSetorForm();
        } else {
            showMessage('Erro ao cadastrar setor: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showMessage('Erro ao cadastrar setor', 'error');
    });
}

function saveEquipamento() {
    const form = document.getElementById('equipamento-form');
    const formData = new FormData(form);
    
    // Validar campos obrigatórios
    const tag = formData.get('tag');
    const descricao = formData.get('descricao');
    const setor_id = formData.get('setor_id');
    
    if (!tag || !descricao || !setor_id) {
        showMessage('Todos os campos obrigatórios devem ser preenchidos', 'error');
        return;
    }
    
    // A foto é opcional, então não precisa validar
    const foto = formData.get('foto');
    
    fetch('/api/equipamentos', {
        method: 'POST',
        body: formData  // Usar FormData diretamente para suportar upload de arquivo
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Equipamento cadastrado com sucesso!', 'success');
            closeEquipamentoForm();
            // Recarregar a árvore de ativos para mostrar o novo equipamento
            if (typeof loadTreeData === 'function') {
                loadTreeData();
            }
        } else {
            showMessage('Erro ao cadastrar equipamento: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showMessage('Erro ao cadastrar equipamento', 'error');
    });
}

// Função para exibir mensagens
function showMessage(message, type) {
    // Remover mensagem anterior se existir
    const existingMessage = document.querySelector('.message-alert');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Criar nova mensagem
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-alert message-${type}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
    `;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}


// Funções para preview da foto do equipamento
document.addEventListener('DOMContentLoaded', function() {
    const fotoInput = document.getElementById('equipamento-foto');
    if (fotoInput) {
        fotoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validar tipo de arquivo
                if (!file.type.startsWith('image/')) {
                    showMessage('Por favor, selecione apenas arquivos de imagem', 'error');
                    e.target.value = '';
                    return;
                }
                
                // Validar tamanho (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showMessage('A imagem deve ter no máximo 5MB', 'error');
                    e.target.value = '';
                    return;
                }
                
                // Mostrar preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('foto-preview');
                    const previewImg = document.getElementById('foto-preview-img');
                    
                    previewImg.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

function removerFotoPreview() {
    const fotoInput = document.getElementById('equipamento-foto');
    const preview = document.getElementById('foto-preview');
    
    fotoInput.value = '';
    preview.style.display = 'none';
}

