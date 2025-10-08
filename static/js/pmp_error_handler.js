/**
 * Tratamento de Erros Robusto para Sistema PMP
 * Adiciona try/catch e validação de JSON em todas as chamadas
 */

// Função auxiliar para fazer requisições com tratamento de erro
async function fetchWithErrorHandling(url, options = {}) {
    try {
        console.log(`🌐 Fazendo requisição para: ${url}`);
        
        const response = await fetch(url, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        console.log(`📡 Resposta recebida: ${response.status} ${response.statusText}`);
        
        // Verificar se a resposta é OK
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Verificar se o Content-Type é JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('❌ Resposta não é JSON:', text.substring(0, 200));
            throw new Error('Resposta do servidor não é JSON válido');
        }
        
        // Tentar fazer parse do JSON
        const data = await response.json();
        console.log('✅ JSON parseado com sucesso:', data);
        
        return { success: true, data, response };
        
    } catch (error) {
        console.error('❌ Erro na requisição:', error);
        
        // Retornar erro estruturado
        return {
            success: false,
            error: error.message,
            type: error.name
        };
    }
}

// Função melhorada para verificar pendências
async function verificarOSPendentesPMPSeguro() {
    try {
        console.log('🔍 Verificando OS pendentes de PMP (versão segura)...');
        
        const result = await fetchWithErrorHandling('/api/pmp/os/verificar-pendencias');
        
        if (!result.success) {
            console.error('❌ Erro na verificação de pendências:', result.error);
            return;
        }
        
        const data = result.data;
        
        if (data.success && data.resumo && data.resumo.total_pmps_com_pendencias > 0) {
            console.log(`⚠️ ${data.resumo.total_pmps_com_pendencias} PMPs com pendências encontradas`);
            
            // Mostrar detalhes das pendências
            if (data.pendencias && Array.isArray(data.pendencias)) {
                data.pendencias.forEach(pendencia => {
                    console.log(`📋 ${pendencia.pmp_codigo}: ${pendencia.os_pendentes} OS pendentes (${pendencia.frequencia})`);
                });
            }
            
            // Gerar OS pendentes automaticamente
            await gerarOSPendentesSeguro();
            
        } else {
            console.log('✅ Nenhuma OS pendente de PMP encontrada');
        }
        
    } catch (error) {
        console.error('❌ Erro crítico ao verificar OS pendentes:', error);
    }
}

// Função melhorada para gerar OS
async function gerarOSPendentesSeguro() {
    try {
        console.log('🚀 Gerando OS pendentes (versão segura)...');
        
        const result = await fetchWithErrorHandling('/api/pmp/os/gerar-todas', {
            method: 'POST'
        });
        
        if (!result.success) {
            console.error('❌ Erro na geração de OS:', result.error);
            return;
        }
        
        const data = result.data;
        
        if (data.success && data.estatisticas) {
            const osGeradas = data.estatisticas.os_geradas || 0;
            const pmpsProcessadas = data.estatisticas.pmps_processadas || 0;
            
            console.log(`✅ ${osGeradas} OS geradas automaticamente para ${pmpsProcessadas} PMPs`);
            
            // Recarregar a programação após gerar OS
            if (osGeradas > 0) {
                console.log('🔄 Recarregando programação com novas OS...');
                setTimeout(() => {
                    if (typeof loadOrdensServico === 'function') {
                        loadOrdensServico();
                    } else if (typeof loadData === 'function') {
                        loadData();
                    }
                }, 2000);
            }
        } else {
            console.error('❌ Erro na geração automática:', data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('❌ Erro crítico ao gerar OS:', error);
    }
}

// Função melhorada para execução automática
async function executarVerificacaoAutomaticaPMPSeguro() {
    try {
        console.log('🤖 Executando verificação automática de PMPs (versão segura)');
        
        const result = await fetchWithErrorHandling('/api/pmp/os/executar-automatico', {
            method: 'POST'
        });
        
        if (!result.success) {
            console.error('❌ Erro na execução automática:', result.error);
            
            // Fallback: tentar verificação manual
            console.log('🔄 Tentando fallback com verificação manual...');
            await verificarOSPendentesPMPSeguro();
            return;
        }
        
        const data = result.data;
        
        if (data.success && data.estatisticas) {
            const osGeradas = data.estatisticas.os_geradas || 0;
            console.log(`✅ Verificação automática concluída: ${osGeradas} OS geradas`);
            
            // Mostrar notificação apenas se OS foram geradas
            if (osGeradas > 0 && typeof showNotification === 'function') {
                showNotification(`🤖 Sistema automático gerou ${osGeradas} OS de PMPs`, 'success');
                
                // Recarregar dados da programação para mostrar novas OS
                setTimeout(() => {
                    if (typeof loadData === 'function') {
                        loadData();
                    }
                }, 2000);
            }
        } else {
            console.warn('⚠️ Erro na verificação automática:', data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('❌ Erro crítico na verificação automática:', error);
    } finally {
        // Sempre atualizar indicador
        if (typeof updatePMPStatusIndicator === 'function') {
            updatePMPStatusIndicator();
        }
    }
}

// Função para verificar status do sistema automático
async function verificarStatusSistemaAutomatico() {
    try {
        const result = await fetchWithErrorHandling('/api/pmp/auto/status');
        
        if (result.success && result.data.success) {
            return result.data.status;
        } else {
            console.warn('⚠️ Não foi possível obter status do sistema automático');
            return null;
        }
        
    } catch (error) {
        console.error('❌ Erro ao verificar status do sistema:', error);
        return null;
    }
}

// Substituir funções originais pelas versões seguras
if (typeof window !== 'undefined') {
    // Sobrescrever funções globais com versões seguras
    window.verificarOSPendentesPMP = verificarOSPendentesPMPSeguro;
    window.executarVerificacaoAutomaticaPMP = executarVerificacaoAutomaticaPMPSeguro;
    window.verificarStatusSistemaAutomatico = verificarStatusSistemaAutomatico;
    
    console.log('🛡️ Sistema de tratamento de erros PMP carregado');
}
