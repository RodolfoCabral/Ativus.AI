# 🔧 INSTRUÇÕES PARA MIGRAÇÃO CORRIGIDA DO BANCO

## 🚨 **PROBLEMA IDENTIFICADO**

O script de migração anterior falhou devido a problemas de transação no PostgreSQL. Quando um comando SQL falha em uma transação, todos os comandos subsequentes são ignorados até que a transação seja finalizada.

## ✅ **SOLUÇÃO IMPLEMENTADA**

Criamos dois scripts corrigidos que tratam adequadamente as transações:

### **1. 📄 migracoes_banco_corrigidas.py**
- Script completo com verificação de existência de colunas
- Cada comando executa em sua própria transação
- Relatório detalhado de sucesso/falha
- Verificação final da estrutura

### **2. 📄 migrar_banco_simples.py**
- Script simplificado para execução rápida
- Usa `IF NOT EXISTS` quando possível
- Ignora erros de "já existe"
- Ideal para execução no Heroku

## 🚀 **COMO EXECUTAR NO HEROKU**

### **Opção 1: Script Simples (Recomendado)**
```bash
heroku run python migrar_banco_simples.py -a ativusai
```

### **Opção 2: Script Completo**
```bash
heroku run python migracoes_banco_corrigidas.py -a ativusai
```

## 📋 **O QUE OS SCRIPTS FAZEM**

### **Colunas Adicionadas à `ordens_servico`:**
- `pmp_id` - INTEGER (FK para tabela pmps)
- `data_proxima_geracao` - DATE (controle de frequência)
- `frequencia_origem` - VARCHAR(20) (tipo de frequência)
- `numero_sequencia` - INTEGER DEFAULT 1 (contador de OS)

### **Colunas Adicionadas à `pmps`:**
- `hora_homem` - DECIMAL(10,2) (horas-homem calculadas)
- `materiais` - TEXT (lista de materiais em JSON)
- `usuarios_responsaveis` - TEXT (lista de usuários em JSON)
- `data_inicio_plano` - DATE (data de início do plano)
- `data_fim_plano` - DATE (data de fim do plano)
- `os_geradas_count` - INTEGER DEFAULT 0 (contador de OS geradas)

### **Índices Criados:**
- `idx_ordens_servico_pmp_id` - Para performance em consultas por PMP
- `idx_ordens_servico_data_programada` - Para consultas por data
- `idx_pmps_data_inicio` - Para consultas por data de início

## 🎯 **RESULTADO ESPERADO**

Após executar o script, você deve ver:

```
✅ Adicionar coluna pmp_id
✅ Adicionar coluna data_proxima_geracao
✅ Adicionar coluna frequencia_origem
✅ Adicionar coluna numero_sequencia
✅ Adicionar coluna hora_homem
✅ Adicionar coluna materiais
✅ Adicionar coluna usuarios_responsaveis
✅ Adicionar coluna data_inicio_plano
✅ Adicionar coluna data_fim_plano
✅ Adicionar coluna os_geradas_count
✅ Criar índice pmp_id
✅ Criar índice data_programada
✅ Criar índice data_inicio_plano

📊 RESULTADO: 13/13 operações bem-sucedidas
🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!
🚀 BANCO PRONTO PARA O SISTEMA PMP/OS!
```

## ⚠️ **SE ALGUMAS COLUNAS JÁ EXISTEM**

Você pode ver mensagens como:
```
⚠️ Adicionar coluna pmp_id - já existe
```

Isso é normal e indica que a coluna já foi criada anteriormente.

## 🔍 **VERIFICAÇÃO APÓS MIGRAÇÃO**

Para verificar se tudo funcionou, você pode executar:

```bash
heroku run python -c "
from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    # Verificar ordens_servico
    cols_os = [col['name'] for col in inspector.get_columns('ordens_servico')]
    print('Colunas ordens_servico:', 'pmp_id' in cols_os, 'data_proxima_geracao' in cols_os)
    
    # Verificar pmps
    cols_pmps = [col['name'] for col in inspector.get_columns('pmps')]
    print('Colunas pmps:', 'data_inicio_plano' in cols_pmps, 'usuarios_responsaveis' in cols_pmps)
" -a ativusai
```

## 🎉 **APÓS A MIGRAÇÃO**

Uma vez que a migração seja bem-sucedida:

1. ✅ O sistema PMP/OS estará totalmente funcional
2. ✅ Todas as APIs de geração automática funcionarão
3. ✅ O módulo de analytics estará operacional
4. ✅ A integração com a programação funcionará perfeitamente

## 📞 **SUPORTE**

Se ainda houver problemas após executar os scripts corrigidos, verifique:

1. **Logs do Heroku:** `heroku logs --tail -a ativusai`
2. **Conexão com banco:** Verificar se o PostgreSQL está acessível
3. **Permissões:** Verificar se o usuário tem permissão para ALTER TABLE

Os scripts foram projetados para serem robustos e lidar com a maioria dos cenários de erro.

