// Dados globais
let equipamentosData = [];
let filiaisData = [];
let setoresData = [];
let equipamentosFiltrados = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Iniciando Lista de QR Codes');
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
        
        // Carregar todos os setores
        const setoresResponse = await fetch('/api/setores');
        if (setoresResponse.ok) {
            const setoresResult = await setoresResponse.json();
            setoresData = setoresResult.setores || [];
            console.log(`🏭 ${setoresData.length} setores carregados`);
        }
        
        // Carregar todos os equipamentos
        const equipamentosResponse = await fetch('/api/equipamentos');
        if (equipamentosResponse.ok) {
            const equipamentosResult = await equipamentosResponse.json();
            equipamentosData = equipamentosResult.equipamentos || [];
            console.log(`⚙️ ${equipamentosData.length} equipamentos carregados`);
            
            // Inicializar com todos os equipamentos
            equipamentosFiltrados = [...equipamentosData];
            atualizarEstatisticas();
            renderizarQRCodes();
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
function carregarSetores() {
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
function carregarEquipamentos() {
    const filialId = document.getElementById('filial-filter').value;
    const setorId = document.getElementById('setor-filter').value;
    
    console.log(`🔄 Filtrando equipamentos - Filial: ${filialId || 'todas'}, Setor: ${setorId || 'todos'}`);
    
    try {
        equipamentosFiltrados = equipamentosData.filter(equipamento => {
            let incluir = true;
            
            // Filtrar por setor se selecionado
            if (setorId && equipamento.setor_id != setorId) {
                incluir = false;
            }
            
            // Filtrar por filial se selecionada (através do setor)
            if (filialId && incluir) {
                const setor = setoresData.find(s => s.id === equipamento.setor_id);
                if (!setor || setor.filial_id != filialId) {
                    incluir = false;
                }
            }
            
            return incluir;
        });
        
        console.log(`⚙️ ${equipamentosFiltrados.length} equipamentos filtrados`);
        
        atualizarEstatisticas();
        renderizarQRCodes();
        
    } catch (error) {
        console.error('❌ Erro ao filtrar equipamentos:', error);
    }
}

// Atualizar estatísticas
function atualizarEstatisticas() {
    document.getElementById('total-equipamentos').textContent = equipamentosFiltrados.length;
    
    // Contar filiais únicas dos equipamentos filtrados
    const filiaisUnicas = new Set();
    const setoresUnicos = new Set();
    
    equipamentosFiltrados.forEach(equipamento => {
        const setor = setoresData.find(s => s.id === equipamento.setor_id);
        if (setor) {
            setoresUnicos.add(setor.id);
            filiaisUnicas.add(setor.filial_id);
        }
    });
    
    document.getElementById('total-filiais').textContent = filiaisUnicas.size;
    document.getElementById('total-setores').textContent = setoresUnicos.size;
}

// Renderizar QR codes
function renderizarQRCodes() {
    const container = document.getElementById('qr-container');
    
    if (equipamentosFiltrados.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>Nenhum equipamento encontrado</h3>
                <p>Tente ajustar os filtros para ver mais resultados</p>
            </div>
        `;
        return;
    }
    
    // Mostrar loading
    container.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <h3>Gerando QR Codes...</h3>
            <p>Processando ${equipamentosFiltrados.length} equipamentos</p>
        </div>
    `;
    
    // Gerar QR codes após um pequeno delay para mostrar o loading
    setTimeout(() => {
        const qrGrid = document.createElement('div');
        qrGrid.className = 'qr-grid';
        
        equipamentosFiltrados.forEach((equipamento, index) => {
            const qrCard = criarCardQR(equipamento, index);
            qrGrid.appendChild(qrCard);
        });
        
        container.innerHTML = '';
        container.appendChild(qrGrid);
        
        // Gerar QR codes após os elementos estarem no DOM
        setTimeout(() => {
            equipamentosFiltrados.forEach((equipamento, index) => {
                gerarQRCode(equipamento, index);
            });
        }, 100);
        
    }, 500);
}

// Criar card de QR code
function criarCardQR(equipamento, index) {
    const setor = setoresData.find(s => s.id === equipamento.setor_id);
    const filial = filiaisData.find(f => f.id === setor?.filial_id);
    
    const card = document.createElement('div');
    card.className = 'qr-card';
    card.innerHTML = `
        <div class="qr-code-container" id="qr-container-${index}">
            <div style="width: 150px; height: 150px; background: #f8f9fa; border: 1px dashed #ddd; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                <i class="fas fa-spinner fa-spin" style="color: #9956a8;"></i>
            </div>
        </div>
        
        <div class="equipment-info">
            <div class="equipment-tag">${equipamento.tag}</div>
            <div class="equipment-description">${equipamento.descricao}</div>
            <div class="equipment-details">
                <div><strong>ID:</strong> ${equipamento.id}</div>
                <div><strong>Setor:</strong> ${setor ? `${setor.tag} - ${setor.descricao}` : 'N/A'}</div>
                <div><strong>Filial:</strong> ${filial ? `${filial.tag} - ${filial.descricao}` : 'N/A'}</div>
                <div><strong>Criado por:</strong> ${equipamento.usuario_criacao || 'Sistema'}</div>
                <div><strong>Data:</strong> ${formatarData(equipamento.data_criacao)}</div>
            </div>
        </div>
    `;
    
    return card;
}

// Gerar QR code para um equipamento
function gerarQRCode(equipamento, index) {
    try {
        console.log(`🔲 Gerando QR Code para equipamento ${equipamento.id} (${index})`);
        
        // Dados do equipamento para o QR Code (mesmo formato da manutenção preventiva)
        const dadosQR = {
            id: equipamento.id,
            tag: equipamento.tag,
            descricao: equipamento.descricao,
            setor_id: equipamento.setor_id,
            tipo: 'equipamento'
        };
        
        // Converter para JSON
        const qrData = JSON.stringify(dadosQR);
        
        // Elemento onde o QR Code será inserido
        const qrContainer = document.getElementById(`qr-container-${index}`);
        
        if (!qrContainer) {
            console.error(`❌ Container do QR Code ${index} não encontrado`);
            return;
        }
        
        // Limpar container
        qrContainer.innerHTML = '';
        
        // Verificar se a biblioteca QRCode está disponível
        if (typeof QRCode !== 'undefined') {
            // Usar biblioteca QRCode.js
            QRCode.toCanvas(qrData, { width: 150, margin: 2 }, function (error, canvas) {
                if (error) {
                    console.error(`❌ Erro ao gerar QR Code ${index}:`, error);
                    mostrarQRCodeErro(qrContainer);
                } else {
                    canvas.style.cssText = 'border: 1px solid #ddd; border-radius: 4px;';
                    canvas.setAttribute('data-equipment-id', equipamento.id);
                    qrContainer.appendChild(canvas);
                    console.log(`✅ QR Code ${index} gerado com sucesso`);
                }
            });
        } else {
            // Fallback: usar API online para gerar QR Code
            const qrCodeURL = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrData)}`;
            
            const img = document.createElement('img');
            img.src = qrCodeURL;
            img.alt = `QR Code do equipamento ${equipamento.tag}`;
            img.style.cssText = 'width: 150px; height: 150px; border: 1px solid #ddd; border-radius: 4px;';
            img.setAttribute('data-equipment-id', equipamento.id);
            img.onload = () => console.log(`✅ QR Code ${index} gerado com sucesso (fallback)`);
            img.onerror = () => mostrarQRCodeErro(qrContainer);
            
            qrContainer.appendChild(img);
        }
        
    } catch (error) {
        console.error(`❌ Erro ao gerar QR Code ${index}:`, error);
        const qrContainer = document.getElementById(`qr-container-${index}`);
        if (qrContainer) {
            mostrarQRCodeErro(qrContainer);
        }
    }
}

// Função auxiliar para mostrar erro no QR Code
function mostrarQRCodeErro(container) {
    container.innerHTML = `
        <div style="
            width: 150px; 
            height: 150px; 
            border: 2px dashed #ccc; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            color: #999;
            font-size: 12px;
            text-align: center;
            border-radius: 4px;
        ">
            <div>
                <i class="fas fa-exclamation-triangle" style="font-size: 20px; margin-bottom: 5px;"></i><br>
                Erro ao gerar<br>QR Code
            </div>
        </div>
    `;
}

// Baixar PDF com todos os QR codes - VERSÃO CORRIGIDA
function baixarPDF() {
    try {
        console.log('📄 Iniciando geração de PDF...');
        
        if (equipamentosFiltrados.length === 0) {
            alert('Nenhum equipamento para gerar PDF. Ajuste os filtros.');
            return;
        }
        
        // Verificar múltiplas formas de acesso ao jsPDF
        let jsPDF = null;
        
        if (typeof window.jsPDF !== 'undefined') {
            jsPDF = window.jsPDF;
            console.log('✅ jsPDF encontrado em window.jsPDF');
        } else if (typeof window.jspdf !== 'undefined' && window.jspdf.jsPDF) {
            jsPDF = window.jspdf.jsPDF;
            console.log('✅ jsPDF encontrado em window.jspdf.jsPDF');
        } else if (typeof jspdf !== 'undefined' && jspdf.jsPDF) {
            jsPDF = jspdf.jsPDF;
            console.log('✅ jsPDF encontrado em jspdf.jsPDF');
        }
        
        if (!jsPDF) {
            console.error('❌ jsPDF não encontrado, tentando carregar dinamicamente...');
            carregarJsPDFDinamicamente();
            return;
        }
        
        // Mostrar mensagem de progresso
        const btnDownload = document.querySelector('.btn-download');
        const originalText = btnDownload.innerHTML;
        btnDownload.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando PDF...';
        btnDownload.disabled = true;
        
        // Aguardar um pouco para garantir que todos os QR codes foram gerados
        setTimeout(() => {
            try {
                const doc = new jsPDF();
                
                // Configurações melhoradas para layout vertical
                const pageWidth = doc.internal.pageSize.getWidth();
                const pageHeight = doc.internal.pageSize.getHeight();
                const margin = 15;
                const qrSize = 40; // QR code menor para melhor layout
                const itemWidth = (pageWidth - 3 * margin) / 2; // 2 colunas
                const itemHeight = 80; // Altura para acomodar informações embaixo
                const itemsPerRow = 2;
                const itemsPerPage = 6; // 3 linhas x 2 colunas
                
                let currentPage = 1;
                let itemCount = 0;
                
                // Título da primeira página
                doc.setFontSize(16);
                doc.setFont(undefined, 'bold');
                doc.text('Lista de QR Codes - Equipamentos', pageWidth / 2, 20, { align: 'center' });
                
                doc.setFontSize(10);
                doc.setFont(undefined, 'normal');
                doc.text(`Total: ${equipamentosFiltrados.length} equipamentos`, pageWidth / 2, 28, { align: 'center' });
                doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, pageWidth / 2, 34, { align: 'center' });
                
                let yPosition = 45;
                
                equipamentosFiltrados.forEach((equipamento, index) => {
                    // Verificar se precisa de nova página
                    if (itemCount > 0 && itemCount % itemsPerPage === 0) {
                        doc.addPage();
                        currentPage++;
                        yPosition = 20;
                        
                        // Título da nova página
                        doc.setFontSize(14);
                        doc.setFont(undefined, 'bold');
                        doc.text(`Lista de QR Codes - Página ${currentPage}`, pageWidth / 2, 15, { align: 'center' });
                        yPosition = 25;
                    }
                    
                    // Calcular posição na grade
                    const col = itemCount % itemsPerRow;
                    const row = Math.floor((itemCount % itemsPerPage) / itemsPerRow);
                    
                    const xPosition = margin + col * (itemWidth + margin);
                    const currentY = yPosition + row * itemHeight;
                    
                    // QR code centralizado horizontalmente no item
                    const qrX = xPosition + (itemWidth - qrSize) / 2;
                    const qrY = currentY;
                    
                    // Tentar obter o QR code do canvas
                    const qrCanvas = document.querySelector(`canvas[data-equipment-id="${equipamento.id}"]`);
                    
                    if (qrCanvas) {
                        try {
                            // Adicionar QR code ao PDF
                            const qrDataURL = qrCanvas.toDataURL('image/png');
                            doc.addImage(qrDataURL, 'PNG', qrX, qrY, qrSize, qrSize);
                            console.log(`✅ QR Code adicionado para equipamento ${equipamento.id}`);
                        } catch (error) {
                            console.warn(`⚠️ Erro ao adicionar QR code do equipamento ${equipamento.id}:`, error);
                            // Adicionar placeholder com borda
                            doc.setDrawColor(150, 150, 150);
                            doc.rect(qrX, qrY, qrSize, qrSize);
                            doc.setFontSize(8);
                            doc.setTextColor(100, 100, 100);
                            doc.text('QR Code', qrX + qrSize/2, qrY + qrSize/2 - 2, { align: 'center' });
                            doc.text('Indisponível', qrX + qrSize/2, qrY + qrSize/2 + 3, { align: 'center' });
                            doc.setTextColor(0, 0, 0); // Voltar para preto
                        }
                    } else {
                        console.warn(`⚠️ Canvas não encontrado para equipamento ${equipamento.id}`);
                        // QR code não encontrado, adicionar placeholder
                        doc.setDrawColor(150, 150, 150);
                        doc.rect(qrX, qrY, qrSize, qrSize);
                        doc.setFontSize(8);
                        doc.setTextColor(100, 100, 100);
                        doc.text('QR Code', qrX + qrSize/2, qrY + qrSize/2 - 2, { align: 'center' });
                        doc.text('Carregando...', qrX + qrSize/2, qrY + qrSize/2 + 3, { align: 'center' });
                        doc.setTextColor(0, 0, 0); // Voltar para preto
                    }
                    
                    // INFORMAÇÕES DO EQUIPAMENTO EMBAIXO DO QR CODE
                    const setor = setoresData.find(s => s.id === equipamento.setor_id);
                    const filial = filiaisData.find(f => f.id === setor?.filial_id);
                    
                    const infoY = qrY + qrSize + 4; // 4mm abaixo do QR code
                    
                    // Tag do equipamento (destaque) - centralizada
                    doc.setFont(undefined, 'bold');
                    doc.setFontSize(10);
                    doc.text(equipamento.tag || 'N/A', xPosition + itemWidth/2, infoY, { align: 'center' });
                    
                    // Descrição - centralizada
                    doc.setFont(undefined, 'normal');
                    doc.setFontSize(8);
                    const descricao = equipamento.descricao || 'Sem descrição';
                    const descricaoTruncada = descricao.length > 28 ? descricao.substring(0, 28) + '...' : descricao;
                    doc.text(descricaoTruncada, xPosition + itemWidth/2, infoY + 5, { align: 'center' });
                    
                    // Informações técnicas organizadas - alinhadas à esquerda
                    doc.setFontSize(7);
                    const infoX = xPosition + 2; // Pequena margem da esquerda
                    doc.text(`ID: ${equipamento.id}`, infoX, infoY + 11);
                    doc.text(`Setor: ${setor ? setor.tag : 'N/A'}`, infoX, infoY + 16);
                    doc.text(`Filial: ${filial ? filial.tag : 'N/A'}`, infoX, infoY + 21);
                    
                    // Data de criação (se disponível)
                    if (equipamento.data_criacao) {
                        const data = formatarData(equipamento.data_criacao);
                        doc.text(`Criado: ${data}`, infoX, infoY + 26);
                    }
                    
                    itemCount++;
                });
                
                // Salvar PDF
                const fileName = `qr-codes-equipamentos-${new Date().toISOString().split('T')[0]}.pdf`;
                doc.save(fileName);
                
                console.log('✅ PDF gerado com sucesso');
                
                // Restaurar botão
                btnDownload.innerHTML = originalText;
                btnDownload.disabled = false;
                
            } catch (error) {
                console.error('❌ Erro ao gerar PDF:', error);
                alert('Erro ao gerar PDF. Tente novamente.');
                
                // Restaurar botão
                btnDownload.innerHTML = originalText;
                btnDownload.disabled = false;
            }
            
        }, 3000); // Aguardar 3 segundos para garantir que QR codes foram gerados
        
    } catch (error) {
        console.error('❌ Erro ao gerar PDF:', error);
        alert('Erro ao gerar PDF. Aguarde os QR codes carregarem completamente e tente novamente.');
    }
}

// Carregar jsPDF dinamicamente se não estiver disponível
function carregarJsPDFDinamicamente() {
    console.log('🔄 Carregando jsPDF dinamicamente...');
    
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/jspdf@latest/dist/jspdf.umd.min.js';
    
    script.onload = function() {
        console.log('✅ jsPDF carregado dinamicamente');
        setTimeout(() => {
            baixarPDF(); // Tentar novamente após carregar
        }, 1000);
    };
    
    script.onerror = function() {
        console.error('❌ Erro ao carregar jsPDF dinamicamente');
        // Tentar fonte alternativa
        const scriptFallback = document.createElement('script');
        scriptFallback.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        
        scriptFallback.onload = function() {
            console.log('✅ jsPDF fallback carregado');
            setTimeout(() => {
                baixarPDF(); // Tentar novamente após carregar fallback
            }, 1000);
        };
        
        scriptFallback.onerror = function() {
            console.error('❌ Todas as fontes de jsPDF falharam');
            alert('Erro ao carregar biblioteca PDF. Verifique sua conexão e tente novamente.');
        };
        
        document.head.appendChild(scriptFallback);
    };
    
    document.head.appendChild(script);
}

// Funções utilitárias
function formatarData(dataString) {
    if (!dataString) return 'Data não disponível';
    
    try {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return 'Data inválida';
    }
}

function mostrarErro(mensagem) {
    const container = document.getElementById('qr-container');
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

