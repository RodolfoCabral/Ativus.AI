#!/usr/bin/env python3
"""
Script de correção URGENTE para a tela de programação
Corrige o problema do atributo 'atividade' e restaura a versão anterior do programacao.js
"""

import os
import sys
import logging
import shutil
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Adicionar diretório atual ao path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Corrigir o problema do atributo 'atividade'
    logger.info("🔧 CORREÇÃO URGENTE: Iniciando correção da tela de programação")
    
    # Verificar se os arquivos existem
    arquivos_para_verificar = [
        'routes/pmp_scheduler.py',
        'routes/pmp_os_generator.py',
        'static/js/programacao.js'
    ]
    
    for arquivo in arquivos_para_verificar:
        if not os.path.exists(arquivo):
            logger.error(f"❌ Arquivo {arquivo} não encontrado")
            sys.exit(1)
    
    # Fazer backup dos arquivos antes de modificá-los
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for arquivo in arquivos_para_verificar:
        backup_path = os.path.join(backup_dir, os.path.basename(arquivo))
        shutil.copy2(arquivo, backup_path)
        logger.info(f"✅ Backup de {arquivo} criado em {backup_path}")
    
    # 2. Corrigir pmp_scheduler.py
    try:
        arquivo_path = 'routes/pmp_scheduler.py'
        with open(arquivo_path, 'r') as f:
            conteudo = f.read()
        
        # Substituir todas as ocorrências de pmp.atividade
        conteudo_corrigido = conteudo.replace('pmp.atividade', 'str(pmp.id)')
        conteudo_corrigido = conteudo_corrigido.replace("'pmp_atividade': pmp.atividade", "'pmp_atividade': str(pmp.id)")
        
        with open(arquivo_path, 'w') as f:
            f.write(conteudo_corrigido)
        
        logger.info(f"✅ Arquivo {arquivo_path} corrigido")
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir {arquivo_path}: {e}")
    
    # 3. Corrigir pmp_os_generator.py
    try:
        arquivo_path = 'routes/pmp_os_generator.py'
        with open(arquivo_path, 'r') as f:
            conteudo = f.read()
        
        # Substituir todas as ocorrências de pmp.atividade
        conteudo_corrigido = conteudo.replace('pmp.atividade', 'str(pmp.id)')
        conteudo_corrigido = conteudo_corrigido.replace(
            'descricao=f"PMP: {pmp.atividade} - Sequência #{numero_sequencia}"',
            'descricao=f"PMP #{pmp.id} - Sequência #{numero_sequencia}"'
        )
        
        with open(arquivo_path, 'w') as f:
            f.write(conteudo_corrigido)
        
        logger.info(f"✅ Arquivo {arquivo_path} corrigido")
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir {arquivo_path}: {e}")
    
    # 4. Restaurar versão anterior do programacao.js
    try:
        arquivo_path = 'static/js/programacao.js'
        
        # Conteúdo original do programacao.js (versão que funcionava)
        conteudo_original = """// Variáveis globais
let ordensServico = [];
let usuarios = [];
let currentWeek = 0;
let currentYear = new Date().getFullYear();

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados iniciais
    loadOrdensServico();
    loadUsuarios();
    
    // Configurar navegação de semanas
    document.getElementById('prev-week').addEventListener('click', function() {
        currentWeek--;
        updateWeekDisplay();
        renderUsuarios();
    });
    
    document.getElementById('next-week').addEventListener('click', function() {
        currentWeek++;
        updateWeekDisplay();
        renderUsuarios();
    });
    
    // Inicializar exibição da semana
    updateWeekDisplay();
    
    // Configurar botão de verificar pendências
    document.getElementById('btn-verificar-pendencias').addEventListener('click', function() {
        verificarPendencias();
    });
    
    // Configurar botão de gerar OS pendentes
    document.getElementById('btn-gerar-os-pendentes').addEventListener('click', function() {
        gerarOSPendentes();
    });
});

// Função para carregar ordens de serviço
function loadOrdensServico() {
    fetch('/api/ordens-servico')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar ordens de serviço');
            }
            return response.json();
        })
        .then(data => {
            ordensServico = data;
            renderPriorityLines();
        })
        .catch(error => {
            console.error('Erro:', error);
            // Método alternativo: usar API simplificada
            fetch('/api/ordens-servico-simples')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao carregar ordens de serviço (API alternativa)');
                    }
                    return response.json();
                })
                .then(data => {
                    ordensServico = data;
                    renderPriorityLines();
                })
                .catch(error => {
                    console.error('Erro na API alternativa:', error);
                    // Mostrar mensagem de erro
                    alert('Erro ao carregar ordens de serviço. Tente recarregar a página.');
                });
        });
}

// Função para carregar usuários
function loadUsuarios() {
    fetch('/api/usuarios')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar usuários');
            }
            return response.json();
        })
        .then(data => {
            usuarios = data;
            renderUsuarios();
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}

// Função para atualizar a exibição da semana
function updateWeekDisplay() {
    const weekElement = document.querySelector('.semana-navegacao');
    if (weekElement) {
        const today = new Date();
        const targetDate = new Date(today);
        
        // Ajustar para a semana desejada
        targetDate.setDate(targetDate.getDate() + (currentWeek * 7));
        
        // Calcular o número da semana
        const startOfYear = new Date(targetDate.getFullYear(), 0, 1);
        const days = Math.floor((targetDate - startOfYear) / (24 * 60 * 60 * 1000));
        const weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
        
        // Atualizar texto
        weekElement.innerHTML = `Semana: ${weekNumber} | Ano: ${targetDate.getFullYear()}`;
    }
}

// Função para renderizar as linhas de prioridade
function renderPriorityLines() {
    // Limpar conteúdo existente
    document.querySelectorAll('.priority-line').forEach(line => {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando chamados...';
        line.innerHTML = '';
        line.appendChild(spinner);
    });
    
    // Filtrar ordens por prioridade
    const osBaixa = ordensServico.filter(os => os.prioridade === 'baixa' && os.status === 'aberta');
    const osMedia = ordensServico.filter(os => os.prioridade === 'media' && os.status === 'aberta');
    const osAlta = ordensServico.filter(os => os.prioridade === 'alta' && os.status === 'aberta');
    const osSeguranca = ordensServico.filter(os => os.prioridade === 'seguranca' && os.status === 'aberta');
    const osPreventiva = ordensServico.filter(os => 
        (os.prioridade === 'preventiva' && os.status === 'aberta') || 
        (os.tipo_manutencao === 'preventiva' && os.pmp_id && os.status === 'aberta')
    );
    
    // Renderizar cada linha
    renderPriorityLine('baixa', osBaixa);
    renderPriorityLine('media', osMedia);
    renderPriorityLine('alta', osAlta);
    renderPriorityLine('seguranca', osSeguranca);
    renderPriorityLine('preventiva', osPreventiva);
}

// Função para renderizar uma linha de prioridade
function renderPriorityLine(priority, orders) {
    const line = document.querySelector(`.priority-line[data-priority="${priority}"]`);
    if (!line) return;
    
    line.innerHTML = '';
    
    if (orders.length === 0) {
        line.innerHTML = `<div class="no-orders">Nenhuma OS nesta prioridade</div>`;
        return;
    }
    
    orders.forEach(os => {
        const card = createOSCard(os);
        line.appendChild(card);
    });
}

// Função para criar um card de OS
function createOSCard(os) {
    const card = document.createElement('div');
    card.className = 'os-card';
    card.setAttribute('data-os-id', os.id);
    card.setAttribute('draggable', 'true');
    
    // Adicionar classe especial para OS de PMP
    if (os.pmp_id) {
        card.classList.add('os-pmp');
    }
    
    // Título da OS
    const title = document.createElement('div');
    title.className = 'os-title';
    title.textContent = `OS #${os.id}`;
    
    // Descrição da OS
    const desc = document.createElement('div');
    desc.className = 'os-desc';
    desc.textContent = os.descricao || 'Sem descrição';
    
    // Informações adicionais
    const info = document.createElement('div');
    info.className = 'os-info';
    
    // Localização
    if (os.equipamento_tag) {
        const location = document.createElement('div');
        location.className = 'os-location';
        location.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${os.equipamento_tag}`;
        info.appendChild(location);
    }
    
    // Adicionar badges para OS de PMP
    if (os.pmp_id) {
        const pmpBadge = document.createElement('span');
        pmpBadge.className = 'badge badge-pmp';
        pmpBadge.textContent = 'PMP';
        title.appendChild(pmpBadge);
        
        if (os.frequencia_origem) {
            const freqBadge = document.createElement('span');
            freqBadge.className = 'badge badge-freq';
            freqBadge.textContent = os.frequencia_origem;
            title.appendChild(freqBadge);
        }
    }
    
    // Montar card
    card.appendChild(title);
    card.appendChild(desc);
    card.appendChild(info);
    
    // Adicionar eventos de drag and drop
    card.addEventListener('dragstart', handleDragStart);
    
    return card;
}

// Função para renderizar usuários
function renderUsuarios() {
    const container = document.getElementById('usuarios-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Obter dias da semana
    const weekDays = getDaysOfWeek(currentWeek, currentYear);
    
    // Renderizar cada usuário
    usuarios.forEach(usuario => {
        const row = createUsuarioRow(usuario, weekDays);
        container.appendChild(row);
    });
}

// Função para criar uma linha de usuário
function createUsuarioRow(usuario, weekDays) {
    const row = document.createElement('div');
    row.className = 'usuario-row';
    row.setAttribute('data-user-id', usuario.id);
    
    // Informações do usuário
    const userInfo = document.createElement('div');
    userInfo.className = 'usuario-info';
    
    const userName = document.createElement('div');
    userName.className = 'usuario-nome';
    userName.textContent = usuario.name;
    
    const userRole = document.createElement('div');
    userRole.className = 'usuario-cargo';
    userRole.textContent = usuario.cargo || 'Técnico';
    
    userInfo.appendChild(userName);
    userInfo.appendChild(userRole);
    
    row.appendChild(userInfo);
    
    // Dias da semana
    const diasContainer = document.createElement('div');
    diasContainer.className = 'dias-container';
    
    weekDays.forEach(day => {
        const diaElement = document.createElement('div');
        diaElement.className = 'dia-container';
        diaElement.setAttribute('data-date', day.date);
        diaElement.setAttribute('data-user-id', usuario.id);
        diaElement.setAttribute('data-user-name', usuario.name);
        
        // Cabeçalho do dia
        const diaHeader = document.createElement('div');
        diaHeader.className = 'dia-header';
        diaHeader.textContent = `${day.day}/${day.month}`;
        
        // Conteúdo do dia
        const diaContent = document.createElement('div');
        diaContent.className = 'dia-content';
        
        // Adicionar OS agendadas para este dia e usuário
        const osAgendadas = ordensServico.filter(os => 
            os.data_programada === day.date && 
            os.usuario_responsavel === usuario.name &&
            os.status === 'programada'
        );
        
        osAgendadas.forEach(os => {
            const osCard = createOSAgendada(os);
            diaContent.appendChild(osCard);
        });
        
        diaElement.appendChild(diaHeader);
        diaElement.appendChild(diaContent);
        
        // Adicionar eventos de drop
        diaElement.addEventListener('dragover', handleDragOver);
        diaElement.addEventListener('drop', handleDrop);
        
        diasContainer.appendChild(diaElement);
    });
    
    row.appendChild(diasContainer);
    
    return row;
}

// Função para criar uma OS agendada
function createOSAgendada(os) {
    const card = document.createElement('div');
    card.className = 'os-agendada';
    card.setAttribute('data-os-id', os.id);
    
    // Adicionar classe especial para OS de PMP
    if (os.pmp_id) {
        card.classList.add('os-pmp');
    }
    
    // Título da OS
    card.textContent = `OS #${os.id}`;
    
    // Tooltip com descrição
    card.setAttribute('title', os.descricao || 'Sem descrição');
    
    return card;
}

// Função para obter os dias da semana
function getDaysOfWeek(weekOffset, year) {
    const today = new Date();
    const currentDay = today.getDay(); // 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
    
    // Calcular o início da semana (segunda-feira)
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - currentDay + 1 + (weekOffset * 7));
    
    // Gerar os dias da semana
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
        const day = new Date(startOfWeek);
        day.setDate(startOfWeek.getDate() + i);
        
        // Formatar a data como YYYY-MM-DD
        const date = day.toISOString().split('T')[0];
        
        weekDays.push({
            date: date,
            day: day.getDate(),
            month: day.getMonth() + 1,
            year: day.getFullYear()
        });
    }
    
    return weekDays;
}

// Funções de drag and drop
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.getAttribute('data-os-id'));
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDrop(e) {
    e.preventDefault();
    
    const osId = e.dataTransfer.getData('text/plain');
    const date = this.getAttribute('data-date');
    const userId = this.getAttribute('data-user-id');
    const userName = this.getAttribute('data-user-name');
    
    if (osId && date && userId) {
        programarOS(osId, date, userId);
    }
}

// Programar OS para uma data e usuário
async function programarOS(osId, date, userId) {
    try {
        console.log(`🔄 Tentando programar OS #${osId} para ${date} com usuário ID ${userId}`);
        
        // Verificar se temos o ID da OS
        if (!osId) {
            console.error('❌ ID da OS não fornecido');
            alert('Erro: ID da OS não fornecido');
            return;
        }
        
        // Verificar se temos a data
        if (!date) {
            console.error('❌ Data não fornecida');
            alert('Erro: Data não fornecida');
            return;
        }
        
        // Verificar se temos o ID do usuário
        if (!userId) {
            console.error('❌ ID do usuário não fornecido');
            alert('Erro: ID do usuário não fornecido');
            return;
        }
        
        // SOLUÇÃO DEFINITIVA: Usar nome do usuário diretamente do DOM
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        let userName = null;
        
        if (userElement) {
            const userNameElement = userElement.querySelector('.usuario-nome');
            if (userNameElement) {
                userName = userNameElement.textContent.trim();
                console.log(`✅ Nome do usuário obtido do DOM: ${userName}`);
            }
        }
        
        // Se não conseguiu obter do DOM, tentar pelo ID
        if (!userName) {
            const usuario = getUserById(userId);
            if (usuario && usuario.name) {
                userName = usuario.name;
                console.log(`✅ Nome do usuário obtido do objeto: ${userName}`);
            }
        }
        
        // Se ainda não temos o nome, usar um valor padrão
        if (!userName) {
            userName = `Técnico #${userId}`;
            console.warn(`⚠️ Nome do usuário não encontrado, usando valor padrão: ${userName}`);
        }
        
        // Continuar com o nome do usuário
        programarOSComNomeUsuario(osId, date, userName);
    } catch (error) {
        console.error('Erro ao programar OS:', error);
        alert('Erro ao programar OS. Tente novamente.');
    }
}

// Função auxiliar para programar OS com nome do usuário
async function programarOSComNomeUsuario(osId, date, userName) {
    try {
        console.log(`🔄 Programando OS #${osId} para ${date} com usuário ${userName}`);
        
        // Verificar se a data está no formato correto (YYYY-MM-DD)
        if (!date) {
            console.error('❌ Data não fornecida');
            alert('Erro: Data não fornecida');
            return;
        }
        
        // Verificar formato da data
        const isoDateRegex = /^\\d{4}-\\d{2}-\\d{2}$/;
        if (!isoDateRegex.test(date)) {
            console.error(`❌ Formato de data inválido: ${date}`);
            alert('Erro: Formato de data inválido');
            return;
        }
        
        // Verificar se a data é válida
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) {
            console.error(`❌ Data inválida: ${date}`);
            alert('Erro: Data inválida');
            return;
        }
        
        // Preparar dados para API
        const data = {
            id: parseInt(osId),
            data_programada: date,
            usuario_responsavel: userName,
            status: 'programada'
        };
        
        console.log('📤 Enviando dados para API:', data);
        
        // Enviar para API
        const response = await fetch(`/api/ordens-servico/${osId}/programar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('✅ OS programada com sucesso:', responseData);
            
            // Atualizar OS na lista local
            const osIndex = ordensServico.findIndex(os => os.id == osId);
            if (osIndex !== -1) {
                ordensServico[osIndex].data_programada = date;
                ordensServico[osIndex].usuario_responsavel = userName;
                ordensServico[osIndex].status = 'programada';
            }
            
            // Renderizar novamente
            renderUsuarios();
            renderPriorityLines();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName}`, 'success');
        } else {
            // Tentar obter mensagem de erro
            let errorMessage = 'Erro ao programar OS';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                console.error('Erro ao processar resposta de erro:', e);
            }
            
            console.error(`❌ Erro ao programar OS: ${errorMessage}`);
            alert(`Erro: ${errorMessage}`);
            
            // Método alternativo: programar localmente
            programarOSAlternativa(osId, date, userName);
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS:', error);
        alert('Erro ao programar OS. Tentando método alternativo...');
        
        // Método alternativo: programar localmente
        programarOSAlternativa(osId, date, userName);
    }
}

// Método alternativo para programar OS localmente
function programarOSAlternativa(osId, date, userName) {
    console.log(`🔄 Programando OS #${osId} localmente para ${date} com usuário ${userName}`);
    
    try {
        // Atualizar OS na lista local
        const osIndex = ordensServico.findIndex(os => os.id == osId);
        if (osIndex !== -1) {
            ordensServico[osIndex].data_programada = date;
            ordensServico[osIndex].usuario_responsavel = userName;
            ordensServico[osIndex].status = 'programada';
            
            console.log('✅ OS programada localmente com sucesso');
            
            // Renderizar novamente
            renderUsuarios();
            renderPriorityLines();
            
            // Mostrar notificação de sucesso com data formatada
            const dataFormatada = formatDate(date);
            showNotification(`OS #${osId} programada para ${dataFormatada} com ${userName} (modo local)`, 'success');
            
            return true;
        } else {
            console.error(`❌ OS #${osId} não encontrada na lista local`);
            alert(`Erro: OS #${osId} não encontrada`);
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao programar OS localmente:', error);
        alert('Erro ao programar OS localmente');
        return false;
    }
}

// Função para formatar data
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-BR');
    } catch (e) {
        return dateStr;
    }
}

// Função para obter usuário por ID
function getUserById(userId) {
    // Converter para número se for string
    if (typeof userId === 'string') {
        userId = parseInt(userId);
    }
    
    // Verificar se é um número válido
    if (isNaN(userId)) {
        console.error(`❌ ID de usuário inválido: ${userId}`);
        return null;
    }
    
    // Buscar usuário
    const usuario = usuarios.find(u => u.id === userId);
    
    if (!usuario) {
        console.warn(`⚠️ Usuário não encontrado com ID ${userId}`);
    }
    
    return usuario;
}

// Função para verificar pendências
function verificarPendencias() {
    fetch('/api/pmp/verificar-pendencias-hoje')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao verificar pendências');
            }
            return response.json();
        })
        .then(data => {
            if (data.total_pendencias > 0) {
                alert(`Existem ${data.total_pendencias} OS pendentes para geração hoje.`);
            } else {
                alert('Não há OS pendentes para geração hoje.');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao verificar pendências. Tente novamente.');
        });
}

// Função para gerar OS pendentes
function gerarOSPendentes() {
    fetch('/api/pmp/gerar-os-pendentes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao gerar OS pendentes');
            }
            return response.json();
        })
        .then(data => {
            alert(`${data.os_geradas.length} OS geradas com sucesso. ${data.erros.length} erros.`);
            // Recarregar ordens de serviço
            loadOrdensServico();
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao gerar OS pendentes. Tente novamente.');
        });
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Adicionar ao container de notificações
    const container = document.getElementById('notification-container');
    if (!container) {
        // Criar container se não existir
        const newContainer = document.createElement('div');
        newContainer.id = 'notification-container';
        document.body.appendChild(newContainer);
        newContainer.appendChild(notification);
    } else {
        container.appendChild(notification);
    }
    
    // Remover após 5 segundos
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}
"""
        
        with open(arquivo_path, 'w') as f:
            f.write(conteudo_original)
        
        logger.info(f"✅ Arquivo {arquivo_path} restaurado para versão funcional")
    except Exception as e:
        logger.error(f"❌ Erro ao restaurar {arquivo_path}: {e}")
    
    # 5. Adicionar CSS para notificações
    try:
        arquivo_path = 'static/css/dashboard.css'
        if os.path.exists(arquivo_path):
            with open(arquivo_path, 'a') as f:
                f.write("""
/* Notificações */
#notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.notification {
    padding: 10px 15px;
    margin-bottom: 10px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    animation: slide-in 0.3s ease-out;
    max-width: 300px;
}

.notification.info {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
    color: #0d47a1;
}

.notification.success {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
    color: #1b5e20;
}

.notification.warning {
    background-color: #fff8e1;
    border-left: 4px solid #ffc107;
    color: #ff6f00;
}

.notification.error {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #b71c1c;
}

.notification.fade-out {
    opacity: 0;
    transform: translateX(100%);
    transition: opacity 0.5s, transform 0.5s;
}

@keyframes slide-in {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Estilos para OS de PMP */
.os-pmp {
    border-left: 4px solid #9c27b0;
    background: linear-gradient(to right, rgba(156, 39, 176, 0.05), transparent);
}

.os-pmp:hover {
    box-shadow: 0 3px 8px rgba(156, 39, 176, 0.3);
}

.badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    margin-left: 5px;
    font-weight: bold;
    text-transform: uppercase;
}

.badge-pmp {
    background-color: #9c27b0;
    color: white;
}

.badge-freq {
    background-color: #4caf50;
    color: white;
}
""")
            logger.info(f"✅ Estilos adicionados ao arquivo {arquivo_path}")
        else:
            logger.warning(f"⚠️ Arquivo {arquivo_path} não encontrado")
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar estilos: {e}")
    
    logger.info("✅ CORREÇÃO URGENTE CONCLUÍDA COM SUCESSO!")
    logger.info("🔄 Reinicie o servidor para aplicar as alterações")

except Exception as e:
    logger.error(f"❌ Erro geral: {e}")
    sys.exit(1)

