// Variáveis globais
let html5QrCode = null;
let currentCameraId = null;
let cameras = [];
let isScanning = false;
let scannedEquipment = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Iniciando Scanner QR');
    initializeScanner();
    setupEventListeners();
});

// Configurar event listeners
function setupEventListeners() {
    document.getElementById('start-scanner').addEventListener('click', startScanner);
    document.getElementById('stop-scanner').addEventListener('click', stopScanner);
    document.getElementById('switch-camera').addEventListener('click', switchCamera);
    document.getElementById('scan-again').addEventListener('click', scanAgain);
    document.getElementById('btn-abrir-chamado').addEventListener('click', abrirChamado);
    document.getElementById('btn-ordem-servico').addEventListener('click', abrirOrdemServico);
}

// Inicializar scanner
async function initializeScanner() {
    try {
        console.log('🔧 Inicializando HTML5 QR Code Scanner...');
        
        // Verificar se o navegador suporta getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showStatus('error', 'Seu navegador não suporta acesso à câmera. Use um navegador mais recente.');
            return;
        }
        
        // Listar câmeras disponíveis
        await getCameras();
        
        showStatus('waiting', 'Scanner pronto. Clique em "Iniciar Scanner" para começar.');
        
    } catch (error) {
        console.error('❌ Erro ao inicializar scanner:', error);
        showStatus('error', 'Erro ao inicializar o scanner. Verifique as permissões da câmera.');
    }
}

// Obter lista de câmeras
async function getCameras() {
    try {
        cameras = await Html5Qrcode.getCameras();
        console.log(`📷 ${cameras.length} câmeras encontradas:`, cameras);
        
        if (cameras.length === 0) {
            showStatus('error', 'Nenhuma câmera encontrada no dispositivo.');
            return;
        }
        
        // Preferir câmera traseira se disponível
        currentCameraId = cameras.find(camera => 
            camera.label.toLowerCase().includes('back') || 
            camera.label.toLowerCase().includes('traseira')
        )?.id || cameras[0].id;
        
        console.log(`📷 Câmera selecionada: ${currentCameraId}`);
        
        // Mostrar botão de trocar câmera se houver múltiplas
        if (cameras.length > 1) {
            document.getElementById('switch-camera').classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('❌ Erro ao obter câmeras:', error);
        showStatus('error', 'Erro ao acessar câmeras do dispositivo.');
    }
}

// Iniciar scanner
async function startScanner() {
    if (isScanning) return;
    
    try {
        console.log('▶️ Iniciando scanner...');
        showStatus('scanning', 'Iniciando câmera... Posicione o QR code na frente da câmera.');
        
        // Mostrar aviso de permissões
        document.getElementById('camera-permissions').classList.remove('hidden');
        
        // Configurações do scanner
        const config = {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0,
            disableFlip: false
        };
        
        // Inicializar HTML5 QR Code
        html5QrCode = new Html5Qrcode("qr-reader");
        
        // Iniciar scanner
        await html5QrCode.start(
            currentCameraId,
            config,
            onScanSuccess,
            onScanFailure
        );
        
        isScanning = true;
        updateScannerControls();
        
        // Esconder aviso de permissões após sucesso
        setTimeout(() => {
            document.getElementById('camera-permissions').classList.add('hidden');
        }, 3000);
        
        showStatus('scanning', 'Scanner ativo. Posicione o QR code do equipamento na área destacada.');
        
    } catch (error) {
        console.error('❌ Erro ao iniciar scanner:', error);
        
        if (error.name === 'NotAllowedError') {
            showStatus('error', 'Permissão de câmera negada. Por favor, permita o acesso à câmera e tente novamente.');
        } else if (error.name === 'NotFoundError') {
            showStatus('error', 'Câmera não encontrada. Verifique se há uma câmera conectada.');
        } else {
            showStatus('error', 'Erro ao iniciar a câmera. Tente novamente ou use outra câmera.');
        }
        
        document.getElementById('camera-permissions').classList.add('hidden');
    }
}

// Parar scanner
async function stopScanner() {
    if (!isScanning || !html5QrCode) return;
    
    try {
        console.log('⏹️ Parando scanner...');
        await html5QrCode.stop();
        html5QrCode = null;
        isScanning = false;
        updateScannerControls();
        
        showStatus('waiting', 'Scanner parado. Clique em "Iniciar Scanner" para escanear novamente.');
        
    } catch (error) {
        console.error('❌ Erro ao parar scanner:', error);
        showStatus('error', 'Erro ao parar o scanner.');
    }
}

// Trocar câmera
async function switchCamera() {
    if (!isScanning || cameras.length <= 1) return;
    
    try {
        console.log('🔄 Trocando câmera...');
        
        // Encontrar próxima câmera
        const currentIndex = cameras.findIndex(camera => camera.id === currentCameraId);
        const nextIndex = (currentIndex + 1) % cameras.length;
        currentCameraId = cameras[nextIndex].id;
        
        console.log(`📷 Nova câmera: ${currentCameraId}`);
        
        // Parar scanner atual
        await html5QrCode.stop();
        
        // Reiniciar com nova câmera
        const config = {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0,
            disableFlip: false
        };
        
        await html5QrCode.start(
            currentCameraId,
            config,
            onScanSuccess,
            onScanFailure
        );
        
        showStatus('scanning', `Câmera trocada. Scanner ativo com ${cameras[nextIndex].label || 'câmera ' + (nextIndex + 1)}.`);
        
    } catch (error) {
        console.error('❌ Erro ao trocar câmera:', error);
        showStatus('error', 'Erro ao trocar câmera. Tente parar e iniciar novamente.');
    }
}

// Callback de sucesso do scan
async function onScanSuccess(decodedText, decodedResult) {
    console.log('✅ QR Code detectado:', decodedText);
    
    try {
        // Parar scanner
        await stopScanner();
        
        // Processar QR code
        await processQRCode(decodedText);
        
    } catch (error) {
        console.error('❌ Erro ao processar QR code:', error);
        showStatus('error', 'Erro ao processar QR code. Tente escanear novamente.');
    }
}

// Callback de falha do scan
function onScanFailure(error) {
    // Não fazer nada - erros de scan são normais durante o processo
    // console.log('Scan em andamento...', error);
}

// Processar QR code escaneado
async function processQRCode(qrData) {
    try {
        console.log('🔍 Processando QR code:', qrData);
        showStatus('scanning', 'QR code detectado! Buscando informações do equipamento...');
        
        // Tentar parsear como JSON primeiro
        let equipmentData = null;
        
        try {
            equipmentData = JSON.parse(qrData);
        } catch (e) {
            // Se não for JSON, assumir que é um ID simples
            equipmentData = { id: qrData, tag: qrData };
        }
        
        // Buscar informações completas do equipamento
        const equipmentInfo = await fetchEquipmentInfo(equipmentData.id || equipmentData.tag);
        
        if (equipmentInfo) {
            scannedEquipment = equipmentInfo;
            displayEquipmentInfo(equipmentInfo);
            showStatus('success', 'Equipamento encontrado! Selecione uma ação abaixo.');
        } else {
            showStatus('error', `Equipamento não encontrado: ${equipmentData.id || equipmentData.tag}`);
            setTimeout(() => {
                scanAgain();
            }, 3000);
        }
        
    } catch (error) {
        console.error('❌ Erro ao processar QR code:', error);
        showStatus('error', 'Erro ao processar QR code. Verifique se é um QR code válido.');
        setTimeout(() => {
            scanAgain();
        }, 3000);
    }
}

// Buscar informações do equipamento
async function fetchEquipmentInfo(equipmentId) {
    try {
        console.log(`📡 Buscando equipamento: ${equipmentId}`);
        
        // Buscar todos os equipamentos
        const response = await fetch('/api/equipamentos');
        if (!response.ok) {
            throw new Error('Erro ao buscar equipamentos');
        }
        
        const data = await response.json();
        const equipamentos = data.equipamentos || [];
        
        // Procurar por ID ou tag
        const equipment = equipamentos.find(eq => 
            eq.id.toString() === equipmentId.toString() || 
            eq.tag === equipmentId
        );
        
        if (equipment) {
            // Buscar informações do setor
            const setorResponse = await fetch('/api/setores');
            if (setorResponse.ok) {
                const setorData = await setorResponse.json();
                const setor = setorData.setores?.find(s => s.id === equipment.setor_id);
                if (setor) {
                    equipment.setor_info = setor;
                }
            }
            
            console.log('✅ Equipamento encontrado:', equipment);
            return equipment;
        }
        
        console.log('❌ Equipamento não encontrado');
        return null;
        
    } catch (error) {
        console.error('❌ Erro ao buscar equipamento:', error);
        return null;
    }
}

// Exibir informações do equipamento
function displayEquipmentInfo(equipment) {
    const resultDiv = document.getElementById('qr-result');
    const infoDiv = document.getElementById('qr-result-info');
    
    const setorInfo = equipment.setor_info ? 
        `${equipment.setor_info.tag} - ${equipment.setor_info.descricao}` : 
        'Setor não encontrado';
    
    infoDiv.innerHTML = `
        <div>
            <strong>Código:</strong>
            <span>${equipment.tag}</span>
        </div>
        <div>
            <strong>Descrição:</strong>
            <span>${equipment.descricao}</span>
        </div>
        <div>
            <strong>Setor:</strong>
            <span>${setorInfo}</span>
        </div>
        <div>
            <strong>ID:</strong>
            <span>${equipment.id}</span>
        </div>
        <div>
            <strong>Criado por:</strong>
            <span>${equipment.usuario_criacao || 'Sistema'}</span>
        </div>
        <div>
            <strong>Data de criação:</strong>
            <span>${formatarData(equipment.data_criacao)}</span>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
    
    // Scroll para o resultado
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Escanear novamente
function scanAgain() {
    document.getElementById('qr-result').classList.add('hidden');
    scannedEquipment = null;
    startScanner();
}

// Abrir chamado
function abrirChamado() {
    if (!scannedEquipment) {
        alert('Nenhum equipamento selecionado!');
        return;
    }
    
    console.log('🎧 Abrindo chamado para equipamento:', scannedEquipment.tag);
    
    // Redirecionar para página de abrir chamado com dados pré-preenchidos
    const params = new URLSearchParams({
        equipamento_id: scannedEquipment.id,
        equipamento_tag: scannedEquipment.tag,
        setor_id: scannedEquipment.setor_id,
        from_scanner: 'true'
    });
    
    window.location.href = `/abrir-chamado?${params.toString()}`;
}

// Abrir ordem de serviço
function abrirOrdemServico() {
    if (!scannedEquipment) {
        alert('Nenhum equipamento selecionado!');
        return;
    }
    
    console.log('🔧 Abrindo ordem de serviço para equipamento:', scannedEquipment.tag);
    
    // Redirecionar para página de programação com dados pré-preenchidos
    const params = new URLSearchParams({
        equipamento_id: scannedEquipment.id,
        equipamento_tag: scannedEquipment.tag,
        setor_id: scannedEquipment.setor_id,
        from_scanner: 'true'
    });
    
    window.location.href = `/programacao?${params.toString()}`;
}

// Atualizar controles do scanner
function updateScannerControls() {
    const startBtn = document.getElementById('start-scanner');
    const stopBtn = document.getElementById('stop-scanner');
    const switchBtn = document.getElementById('switch-camera');
    
    if (isScanning) {
        startBtn.classList.add('hidden');
        stopBtn.classList.remove('hidden');
        if (cameras.length > 1) {
            switchBtn.classList.remove('hidden');
        }
    } else {
        startBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
        switchBtn.classList.add('hidden');
    }
}

// Mostrar status
function showStatus(type, message) {
    const statusDiv = document.getElementById('scanner-status');
    
    // Remover classes anteriores
    statusDiv.className = 'scanner-status';
    
    // Adicionar nova classe
    statusDiv.classList.add(`status-${type}`);
    
    // Definir ícone baseado no tipo
    let icon = 'fas fa-info-circle';
    switch (type) {
        case 'scanning':
            icon = 'fas fa-camera';
            break;
        case 'success':
            icon = 'fas fa-check-circle';
            break;
        case 'error':
            icon = 'fas fa-exclamation-triangle';
            break;
    }
    
    statusDiv.innerHTML = `<i class="${icon}"></i> ${message}`;
}

// Função utilitária para formatar data
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

// Limpar recursos ao sair da página
window.addEventListener('beforeunload', function() {
    if (isScanning && html5QrCode) {
        html5QrCode.stop().catch(console.error);
    }
});

// Tratar erros globais
window.addEventListener('error', function(event) {
    console.error('❌ Erro global:', event.error);
    if (event.error.message.includes('camera') || event.error.message.includes('Camera')) {
        showStatus('error', 'Erro de câmera. Verifique as permissões e tente novamente.');
    }
});

