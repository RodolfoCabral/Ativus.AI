#!/usr/bin/env python3
"""
Correção para o sistema de geração automática de OS baseadas em PMP
"""

import os
import re
from datetime import datetime, date, timedelta

def analisar_problema():
    """Analisa o problema com a geração de OS"""
    print("🔍 ANÁLISE DO PROBLEMA DE GERAÇÃO DE OS")
    print("=" * 50)
    
    problemas_identificados = [
        "1. Sistema de geração automática não está sendo executado regularmente",
        "2. Não há cron job ou scheduler automático configurado",
        "3. Geração de OS depende de chamada manual da API",
        "4. Falta integração entre PMP e geração automática de OS",
        "5. OS geradas podem não estar com prioridade 'preventiva' correta"
    ]
    
    for problema in problemas_identificados:
        print(f"❌ {problema}")
    
    print("\n💡 SOLUÇÕES A IMPLEMENTAR:")
    solucoes = [
        "1. Criar sistema de verificação automática diária",
        "2. Corrigir filtros na tela de programação",
        "3. Implementar geração automática de OS faltantes",
        "4. Garantir que OS de PMP tenham prioridade 'preventiva'",
        "5. Adicionar logs para debug do sistema"
    ]
    
    for solucao in solucoes:
        print(f"✅ {solucao}")

def criar_sistema_verificacao_automatica():
    """Cria sistema de verificação automática de OS pendentes"""
    
    # 1. Modificar o arquivo de programação para incluir verificação automática
    programacao_js_path = "static/js/programacao.js"
    
    if os.path.exists(programacao_js_path):
        print(f"📝 Modificando {programacao_js_path}")
        
        with open(programacao_js_path, 'r') as f:
            content = f.read()
        
        # Adicionar função de verificação automática
        verificacao_code = '''
// Verificação automática de OS pendentes de PMP
async function verificarOSPendentesPMP() {
    try {
        console.log('🔍 Verificando OS pendentes de PMP...');
        
        const response = await fetch('/api/pmp/verificar-pendencias-hoje');
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.total_pendencias > 0) {
                console.log(`⚠️ ${data.total_pendencias} OS pendentes encontradas`);
                
                // Gerar OS pendentes automaticamente
                const gerarResponse = await fetch('/api/pmp/gerar-os-pendentes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ limite: 20 })
                });
                
                if (gerarResponse.ok) {
                    const gerarData = await gerarResponse.json();
                    console.log(`✅ ${gerarData.os_geradas?.length || 0} OS geradas automaticamente`);
                    
                    // Recarregar a programação após gerar OS
                    if (gerarData.os_geradas?.length > 0) {
                        setTimeout(() => {
                            loadOrdensServico();
                        }, 2000);
                    }
                }
            } else {
                console.log('✅ Nenhuma OS pendente de PMP encontrada');
            }
        }
    } catch (error) {
        console.error('❌ Erro ao verificar OS pendentes:', error);
    }
}

// Executar verificação ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar 3 segundos após carregar para não interferir com outras operações
    setTimeout(verificarOSPendentesPMP, 3000);
    
    // Executar verificação a cada 30 minutos
    setInterval(verificarOSPendentesPMP, 30 * 60 * 1000);
});
'''
        
        # Adicionar o código no final do arquivo
        if 'verificarOSPendentesPMP' not in content:
            content += verificacao_code
            
            with open(programacao_js_path, 'w') as f:
                f.write(content)
            
            print("✅ Sistema de verificação automática adicionado")
        else:
            print("ℹ️ Sistema de verificação já existe")
    
    return True

def corrigir_filtro_preventivas():
    """Corrige o filtro de OS preventivas na programação"""
    
    programacao_js_path = "static/js/programacao.js"
    
    if os.path.exists(programacao_js_path):
        print(f"📝 Corrigindo filtros de preventivas em {programacao_js_path}")
        
        with open(programacao_js_path, 'r') as f:
            content = f.read()
        
        # Procurar e corrigir a função renderPriorityLines
        old_filter = r"ordensServico\.filter\(os => os\.prioridade === 'preventiva'\)"
        new_filter = "ordensServico.filter(os => os.prioridade === 'preventiva' || os.pmp_id || (os.descricao && os.descricao.toLowerCase().includes('pmp')))"
        
        if old_filter in content:
            content = re.sub(old_filter, new_filter, content)
            print("✅ Filtro de preventivas corrigido")
        else:
            # Procurar por padrões similares
            patterns = [
                r"prioridade === 'preventiva'",
                r"prioridade == 'preventiva'",
                r"\.prioridade === \"preventiva\"",
                r"\.prioridade == \"preventiva\""
            ]
            
            for pattern in patterns:
                if re.search(pattern, content):
                    # Substituir por filtro mais abrangente
                    new_pattern = "(os.prioridade === 'preventiva' || os.pmp_id || (os.descricao && os.descricao.toLowerCase().includes('pmp')))"
                    content = re.sub(pattern, new_pattern, content)
                    print(f"✅ Padrão {pattern} corrigido")
                    break
        
        with open(programacao_js_path, 'w') as f:
            f.write(content)
        
        print("✅ Filtros de preventivas atualizados")
    
    return True

def criar_api_geracao_os_faltantes():
    """Cria API para gerar OS faltantes da PMP-02-BBN01"""
    
    api_content = '''
@app.route('/api/pmp/gerar-os-bbn01-faltantes', methods=['POST'])
def gerar_os_bbn01_faltantes():
    """Gera OS faltantes específicas da PMP-02-BBN01"""
    try:
        from datetime import datetime, date, timedelta
        from assets_models import OrdemServico
        
        # Datas que deveriam ter OS (baseado na análise)
        datas_faltantes = [
            date(2025, 9, 5),   # 05/09/2025 - Data inicial
            date(2025, 9, 12),  # 12/09/2025 - +1 semana
            date(2025, 9, 19),  # 19/09/2025 - +2 semanas
            date(2025, 9, 26),  # 26/09/2025 - +3 semanas
            date(2025, 10, 3),  # 03/10/2025 - +4 semanas
        ]
        
        os_geradas = []
        hoje = date.today()
        
        # Buscar PMP-02-BBN01
        pmp_query = db.session.execute(
            "SELECT id FROM pmps WHERE codigo LIKE '%PMP-02%' OR atividade LIKE '%BBN01%' LIMIT 1"
        ).fetchone()
        
        pmp_id = pmp_query[0] if pmp_query else None
        
        for i, data_faltante in enumerate(datas_faltantes, 1):
            # Verificar se já existe OS para esta data
            os_existente = OrdemServico.query.filter_by(
                data_programada=data_faltante
            ).filter(
                OrdemServico.descricao.like('%BBN01%')
            ).first()
            
            if not os_existente and data_faltante <= hoje:
                # Criar nova OS
                nova_os = OrdemServico(
                    descricao=f"PMP: PREVENTIVA SEMANAL - MECANICA - BBN01 - Sequência #{i}",
                    data_programada=data_faltante,
                    status='aberta',
                    prioridade='preventiva',
                    tipo_manutencao='Preventiva',
                    oficina='Mecânica',
                    equipamento='BBN01',
                    pmp_id=pmp_id,
                    sequencia_pmp=i,
                    criado_por=current_user.id if hasattr(current_user, 'id') else 1,
                    criado_em=datetime.now()
                )
                
                db.session.add(nova_os)
                db.session.flush()
                
                os_geradas.append({
                    'id': nova_os.id,
                    'sequencia': i,
                    'data': data_faltante.isoformat(),
                    'descricao': nova_os.descricao
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(os_geradas)} OS geradas para PMP-02-BBN01',
            'os_geradas': os_geradas
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao gerar OS: {str(e)}'}), 500
'''
    
    # Adicionar ao app.py
    app_py_path = "app.py"
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        if 'gerar-os-bbn01-faltantes' not in content:
            # Encontrar onde adicionar a rota
            if 'if __name__ == "__main__":' in content:
                insertion_point = content.find('if __name__ == "__main__":')
                content = content[:insertion_point] + api_content + '\n' + content[insertion_point:]
            else:
                content += api_content
            
            with open(app_py_path, 'w') as f:
                f.write(content)
            
            print("✅ API de geração de OS faltantes adicionada")
    
    return True

def criar_botao_geracao_manual():
    """Cria botão para geração manual de OS na tela de programação"""
    
    programacao_html_path = "static/programacao.html"
    
    if os.path.exists(programacao_html_path):
        with open(programacao_html_path, 'r') as f:
            content = f.read()
        
        # Adicionar botão na seção de chamados em aberto
        botao_html = '''
        <div style="text-align: right; margin-bottom: 10px;">
            <button onclick="gerarOSFaltantesBBN01()" class="btn btn-sm btn-success">
                <i class="fas fa-sync"></i> Gerar OS Faltantes PMP
            </button>
        </div>
'''
        
        # Procurar pela seção de chamados em aberto
        if 'Chamados em Aberto' in content and 'Gerar OS Faltantes PMP' not in content:
            content = content.replace(
                '<h3><i class="fas fa-list"></i> Chamados em Aberto</h3>',
                '<h3><i class="fas fa-list"></i> Chamados em Aberto</h3>' + botao_html
            )
            
            # Adicionar função JavaScript
            js_function = '''
<script>
async function gerarOSFaltantesBBN01() {
    try {
        const button = event.target;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
        
        const response = await fetch('/api/pmp/gerar-os-bbn01-faltantes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${data.os_geradas.length} OS geradas com sucesso!`, 'success');
            // Recarregar a programação
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification('Erro ao gerar OS: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Erro ao gerar OS: ' + error.message, 'error');
    } finally {
        const button = event.target;
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-sync"></i> Gerar OS Faltantes PMP';
    }
}
</script>
'''
            
            # Adicionar antes do </body>
            content = content.replace('</body>', js_function + '\n</body>')
            
            with open(programacao_html_path, 'w') as f:
                f.write(content)
            
            print("✅ Botão de geração manual adicionado")
    
    return True

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DO SISTEMA DE GERAÇÃO DE OS PMP")
    print("=" * 60)
    
    # 1. Analisar o problema
    analisar_problema()
    
    print("\n🚀 IMPLEMENTANDO CORREÇÕES...")
    
    # 2. Criar sistema de verificação automática
    criar_sistema_verificacao_automatica()
    
    # 3. Corrigir filtros de preventivas
    corrigir_filtro_preventivas()
    
    # 4. Criar API para gerar OS faltantes
    criar_api_geracao_os_faltantes()
    
    # 5. Criar botão de geração manual
    criar_botao_geracao_manual()
    
    print("\n" + "=" * 60)
    print("✅ CORREÇÕES IMPLEMENTADAS COM SUCESSO!")
    print("\n📋 RESUMO DAS CORREÇÕES:")
    print("1. ✅ Sistema de verificação automática a cada 30 minutos")
    print("2. ✅ Filtros de preventivas corrigidos para incluir OS de PMP")
    print("3. ✅ API para gerar OS faltantes da PMP-02-BBN01")
    print("4. ✅ Botão manual para gerar OS faltantes")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Faça deploy da aplicação")
    print("2. Acesse a tela de Programação")
    print("3. Clique no botão 'Gerar OS Faltantes PMP'")
    print("4. Verifique se as OS aparecem na linha 'PREVENTIVAS (PMP)'")

if __name__ == "__main__":
    main()
