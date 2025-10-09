"""
Verificador de Duplicatas de OS - Sistema Robusto
"""

from datetime import datetime, date, timedelta
from flask import current_app

def verificar_os_existente_robusta(pmp, data_programada, numero_sequencia, OrdemServico):
    """
    Verificação robusta para evitar criação de OS duplicadas
    
    Args:
        pmp: Objeto PMP
        data_programada: Data da OS
        numero_sequencia: Número da sequência
        OrdemServico: Classe do modelo OrdemServico
    
    Returns:
        OrdemServico ou None se não existir
    """
    
    # Lista de verificações em ordem de prioridade
    verificacoes = []
    
    # 1. Verificação por PMP ID + Data Programada (mais específica)
    os_existente = OrdemServico.query.filter_by(
        pmp_id=pmp.id,
        data_programada=data_programada
    ).first()
    
    if os_existente:
        current_app.logger.info(f"🔍 Verificação 1: OS encontrada por PMP+Data - ID {os_existente.id}")
        return os_existente
    
    # 2. Verificação por PMP ID + Número Sequência
    os_existente = OrdemServico.query.filter_by(
        pmp_id=pmp.id,
        numero_sequencia=numero_sequencia
    ).first()
    
    if os_existente:
        current_app.logger.info(f"🔍 Verificação 2: OS encontrada por PMP+Sequência - ID {os_existente.id}")
        return os_existente
    
    # 3. Verificação por descrição contendo código PMP + sequência
    sequencia_str = f"#{numero_sequencia:03d}"
    os_existente = OrdemServico.query.filter(
        OrdemServico.pmp_id == pmp.id,
        OrdemServico.descricao.like(f"%{pmp.codigo}%{sequencia_str}%")
    ).first()
    
    if os_existente:
        current_app.logger.info(f"🔍 Verificação 3: OS encontrada por Descrição - ID {os_existente.id}")
        return os_existente
    
    # 4. Verificação por tipo preventiva + equipamento + data próxima
    data_inicio = data_programada - timedelta(days=1)
    data_fim = data_programada + timedelta(days=1)
    
    os_existente = OrdemServico.query.filter(
        OrdemServico.equipamento_id == pmp.equipamento_id,
        OrdemServico.tipo_manutencao == 'preventiva-periodica',
        OrdemServico.data_criacao >= data_inicio,
        OrdemServico.data_criacao <= data_fim,
        OrdemServico.pmp_id == pmp.id
    ).first()
    
    if os_existente:
        current_app.logger.info(f"🔍 Verificação 4: OS encontrada por Equipamento+Data - ID {os_existente.id}")
        return os_existente
    
    # 5. Verificação por frequência origem + equipamento (última tentativa)
    os_existente = OrdemServico.query.filter(
        OrdemServico.equipamento_id == pmp.equipamento_id,
        OrdemServico.frequencia_origem == pmp.frequencia,
        OrdemServico.pmp_id == pmp.id,
        OrdemServico.numero_sequencia == numero_sequencia
    ).first()
    
    if os_existente:
        current_app.logger.info(f"🔍 Verificação 5: OS encontrada por Frequência+Equipamento - ID {os_existente.id}")
        return os_existente
    
    # Nenhuma OS encontrada
    current_app.logger.info(f"✅ Nenhuma OS existente encontrada para PMP {pmp.codigo} sequência {numero_sequencia}")
    return None

def contar_os_existentes_pmp(pmp_id, OrdemServico):
    """
    Conta quantas OS já existem para uma PMP
    
    Args:
        pmp_id: ID da PMP
        OrdemServico: Classe do modelo OrdemServico
    
    Returns:
        int: Número de OS existentes
    """
    count = OrdemServico.query.filter_by(pmp_id=pmp_id).count()
    current_app.logger.info(f"📊 PMP ID {pmp_id}: {count} OS existentes")
    return count

def limpar_os_duplicadas_pmp(pmp_id, OrdemServico, db):
    """
    Remove OS duplicadas de uma PMP (usar com cuidado)
    
    Args:
        pmp_id: ID da PMP
        OrdemServico: Classe do modelo OrdemServico
        db: Instância do banco de dados
    
    Returns:
        int: Número de OS removidas
    """
    # Buscar todas as OS da PMP
    todas_os = OrdemServico.query.filter_by(pmp_id=pmp_id).all()
    
    # Agrupar por número de sequência
    sequencias_vistas = set()
    os_para_remover = []
    
    for os in todas_os:
        if os.numero_sequencia in sequencias_vistas:
            os_para_remover.append(os)
            current_app.logger.warning(f"🗑️ OS duplicada detectada: ID {os.id}, Sequência {os.numero_sequencia}")
        else:
            sequencias_vistas.add(os.numero_sequencia)
    
    # Remover duplicatas
    for os in os_para_remover:
        db.session.delete(os)
    
    if os_para_remover:
        db.session.commit()
        current_app.logger.info(f"✅ {len(os_para_remover)} OS duplicadas removidas da PMP {pmp_id}")
    
    return len(os_para_remover)
