
nova_os = OrdemServico(
    # Campos obrigatórios básicos
    descricao=descricao,
    tipo_manutencao='preventiva-periodica',
    oficina=pmp.oficina,
    condicao_ativo='funcionando',
    qtd_pessoas=pmp.num_pessoas or 1,
    horas=pmp.tempo_pessoa or 1.0,
    hh=(pmp.num_pessoas or 1) * (pmp.tempo_pessoa or 1.0),
    prioridade='media',
    status='programada',
    
    # Campos de relacionamento obrigatórios
    equipamento_id=pmp.equipamento_id,
    filial_id=1,  # Buscar da PMP ou usar padrão
    setor_id=1,   # Buscar da PMP ou usar padrão
    
    # Campos de empresa e usuário
    empresa='Ativus',
    usuario_criacao='sistema',
    
    # Campos de data
    data_programada=data_programada,
    data_criacao=datetime.now(),
    
    # Campos específicos de PMP
    pmp_id=pmp.id,
    frequencia_origem=pmp.frequencia,
    numero_sequencia=i
)
