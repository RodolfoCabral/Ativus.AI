🔧 GERADOR DE SQL PARA OS BASEADAS EM PMPs
Data/Hora: 2025-10-08 16:32:43

-- EXEMPLO ESPECÍFICO: PMP-03-BBN01
-- ============================================================
-- PMP-03-BBN01: PREVENTIVA SEMANAL - ELETRICA
-- Data início: 2025-09-08
-- Frequência: semanal
-- OS necessárias: 5

-- OS 1: 2025-09-08 (Monday)
INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #001', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-08', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);

-- OS 2: 2025-09-15 (Monday)
INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #002', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-15', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);

-- OS 3: 2025-09-22 (Monday)
INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #003', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-22', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);

-- OS 4: 2025-09-29 (Monday)
INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #004', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-29', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);

-- OS 5: 2025-10-06 (Monday)
INSERT INTO ordens_servico (
    descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo, origem
) VALUES (
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #005', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-10-06', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    'pmp_automatica'
);

-- Total de OS para PMP-03-BBN01: 5
-- Estas são exatamente as OS mencionadas na especificação:
--   1. 2025-09-08
--   2. 2025-09-15
--   3. 2025-09-22
--   4. 2025-09-29
--   5. 2025-10-06


================================================================================

-- SQL PARA GERAR OS BASEADAS EM PMPs
-- Gerado em: 2025-10-08 16:32:43
-- Total de PMPs processadas: 5

-- PMP: PMP-01-BBN01 - PREVENTIVA MENSAL - MECANICA
-- Frequência: mensal, Data início: 2025-09-04
-- OS necessárias: 2

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1001, 
    'PMP: PREVENTIVA MENSAL - MECANICA - Sequência #001', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-04', 
    NOW(), 
    1, 
    133, 
    'PMP-01-BBN01',
    '[67]',
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1002, 
    'PMP: PREVENTIVA MENSAL - MECANICA - Sequência #002', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-04', 
    NOW(), 
    1, 
    133, 
    'PMP-01-BBN01',
    '[67]',
    'pmp_automatica'
);

-- Fim das OS para PMP-01-BBN01
-- ============================================================

-- PMP: PMP-02-BBN01 - PREVENTIVA SEMANAL - MECANICA
-- Frequência: semanal, Data início: 2025-09-05
-- OS necessárias: 5

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1003, 
    'PMP: PREVENTIVA SEMANAL - MECANICA - Sequência #001', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-05', 
    NOW(), 
    1, 
    134, 
    'PMP-02-BBN01',
    '[67]',
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1004, 
    'PMP: PREVENTIVA SEMANAL - MECANICA - Sequência #002', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-12', 
    NOW(), 
    1, 
    134, 
    'PMP-02-BBN01',
    '[67]',
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1005, 
    'PMP: PREVENTIVA SEMANAL - MECANICA - Sequência #003', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-19', 
    NOW(), 
    1, 
    134, 
    'PMP-02-BBN01',
    '[67]',
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1006, 
    'PMP: PREVENTIVA SEMANAL - MECANICA - Sequência #004', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-26', 
    NOW(), 
    1, 
    134, 
    'PMP-02-BBN01',
    '[67]',
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1007, 
    'PMP: PREVENTIVA SEMANAL - MECANICA - Sequência #005', 
    232, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-03', 
    NOW(), 
    1, 
    134, 
    'PMP-02-BBN01',
    '[67]',
    'pmp_automatica'
);

-- Fim das OS para PMP-02-BBN01
-- ============================================================

-- PMP: PMP-03-BBN01 - PREVENTIVA SEMANAL - ELETRICA
-- Frequência: semanal, Data início: 2025-09-08
-- OS necessárias: 5

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1008, 
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #001', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-08', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1009, 
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #002', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-15', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1010, 
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #003', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-22', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1011, 
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #004', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-09-29', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1012, 
    'PMP: PREVENTIVA SEMANAL - ELETRICA - Sequência #005', 
    232, 
    'preventiva-periodica', 
    'eletrica', 
    'programada', 
    'media',
    '2025-10-06', 
    NOW(), 
    1, 
    135, 
    'PMP-03-BBN01',
    NULL,
    'pmp_automatica'
);

-- Fim das OS para PMP-03-BBN01
-- ============================================================

-- PMP: PMP-05-BBN01 - PREVENTIVA DIARIO - CIVIL
-- Frequência: diario, Data início: 2025-09-05
-- OS necessárias: 34

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1013, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #001', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-05', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1014, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #002', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-06', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1015, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #003', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-07', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1016, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #004', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-08', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1017, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #005', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-09', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1018, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #006', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-10', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1019, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #007', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-11', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1020, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #008', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-12', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1021, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #009', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-13', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1022, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #010', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-14', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1023, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #011', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-15', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1024, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #012', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-16', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1025, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #013', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-17', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1026, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #014', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-18', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1027, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #015', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-19', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1028, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #016', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-20', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1029, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #017', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-21', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1030, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #018', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-22', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1031, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #019', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-23', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1032, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #020', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-24', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1033, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #021', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-25', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1034, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #022', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-26', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1035, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #023', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-27', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1036, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #024', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-28', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1037, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #025', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-29', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1038, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #026', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-09-30', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1039, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #027', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-01', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1040, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #028', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-02', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1041, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #029', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-03', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1042, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #030', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-04', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1043, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #031', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-05', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1044, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #032', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-06', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1045, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #033', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-07', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1046, 
    'PMP: PREVENTIVA DIARIO - CIVIL - Sequência #034', 
    232, 
    'preventiva-periodica', 
    'civil', 
    'programada', 
    'media',
    '2025-10-08', 
    NOW(), 
    1, 
    137, 
    'PMP-05-BBN01',
    NULL,
    'pmp_automatica'
);

-- Fim das OS para PMP-05-BBN01
-- ============================================================

-- PMP: PMP-01-MTD01 - PREVENTIVA DIARIO - MECANICA
-- Frequência: diario, Data início: 2025-09-08
-- OS necessárias: 31

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1047, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #001', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-08', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1048, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #002', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-09', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1049, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #003', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-10', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1050, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #004', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-11', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1051, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #005', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-12', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1052, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #006', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-13', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1053, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #007', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-14', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1054, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #008', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-15', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1055, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #009', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-16', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1056, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #010', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-17', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1057, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #011', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-18', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1058, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #012', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-19', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1059, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #013', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-20', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1060, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #014', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-21', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1061, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #015', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-22', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1062, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #016', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-23', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1063, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #017', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-24', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1064, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #018', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-25', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1065, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #019', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-26', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1066, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #020', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-27', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1067, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #021', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-28', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1068, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #022', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-29', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1069, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #023', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-09-30', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1070, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #024', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-01', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1071, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #025', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-02', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1072, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #026', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-03', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1073, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #027', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-04', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1074, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #028', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-05', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1075, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #029', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-06', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1076, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #030', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-07', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

INSERT INTO ordens_servico (
    id, descricao, equipamento_id, tipo, oficina, status, prioridade,
    data_programada, data_criacao, criado_por, pmp_id, pmp_codigo,
    usuarios_responsaveis, origem
) VALUES (
    1077, 
    'PMP: PREVENTIVA DIARIO - MECANICA - Sequência #031', 
    233, 
    'preventiva-periodica', 
    'mecanica', 
    'programada', 
    'media',
    '2025-10-08', 
    NOW(), 
    1, 
    167, 
    'PMP-01-MTD01',
    NULL,
    'pmp_automatica'
);

-- Fim das OS para PMP-01-MTD01
-- ============================================================

-- RESUMO FINAL:
-- Total de OS geradas: 77
-- PMPs processadas: 5
-- 
-- Para executar estes comandos:
-- 1. Conecte-se ao banco de dados PostgreSQL
-- 2. Execute os comandos INSERT acima
-- 3. Verifique se as OS aparecem na tela de programação

================================================================================
💡 INSTRUÇÕES PARA EXECUÇÃO:

1. Copie os comandos SQL gerados acima
2. Conecte-se ao banco de dados PostgreSQL do Heroku
3. Execute os comandos INSERT
4. Verifique a tela de programação para ver as novas OS

Isso criará 77 OS baseadas nas PMPs com data de início.
As OS seguirão exatamente os cronogramas calculados.
================================================================================
