# 🚨 CORREÇÃO DO ERRO 500 - SISTEMA PMP

## 📋 **PROBLEMAS IDENTIFICADOS**

O diagnóstico revelou 3 problemas principais que causam o erro 500:

### **1. ❌ Blueprint PMP não está sendo importado**
```
Aviso: Não foi possível importar pmp_bp: No module named 'routes.pmp'
```
**Causa:** O arquivo `routes/pmp.py` não foi enviado para o Heroku

### **2. ❌ Tabelas PMP não existem no banco**
```
❌ pmps NÃO existe
❌ atividades_pmp NÃO existe  
❌ historico_execucao_pmp NÃO existe
```
**Causa:** Script de criação de tabelas não foi executado

### **3. ❌ Import do módulo `os` faltando**
```
NameError: name 'os' is not defined
```
**Causa:** Import do módulo `os` estava faltando no `app.py`

## ✅ **CORREÇÕES APLICADAS**

### **1. 🔧 Corrigido import no app.py**
- Adicionado `import os` no início do arquivo
- Blueprint PMP agora pode ser importado corretamente

### **2. 📁 Arquivos atualizados:**
```
app.py                       ← Import do 'os' corrigido
routes/pmp.py               ← Blueprint PMP completo
models/pmp.py               ← Modelos PMP atualizados
static/plano-mestre.html    ← Interface PMP integrada
static/js/plano-mestre.js   ← JavaScript PMP
create_pmp_tables_final.py  ← Script de criação de tabelas
```

## 🚀 **INSTRUÇÕES DE DEPLOY**

### **1. Fazer Deploy dos Arquivos:**
```bash
# Extrair o ZIP e copiar os arquivos para o projeto
# Fazer commit e push para o Heroku
git add .
git commit -m "Correção erro 500 PMP - arquivos atualizados"
git push heroku main
```

### **2. Criar Tabelas PMP:**
```bash
# Executar script de criação de tabelas no Heroku
heroku run python create_pmp_tables_final.py -a ativusai
```

### **3. Verificar Deploy:**
```bash
# Verificar logs do Heroku
heroku logs --tail -a ativusai

# Deve aparecer:
# "Blueprint de PMP registrado com sucesso"
```

## 🎯 **RESULTADO ESPERADO**

Após aplicar as correções:

### **✅ Blueprint PMP registrado:**
```
Blueprint de PMP registrado com sucesso
```

### **✅ Rotas PMP funcionais:**
```
POST /api/pmp/equipamento/{id}/gerar  ← Gerar PMPs
GET  /api/pmp/equipamento/{id}        ← Listar PMPs
GET  /api/pmp/{pmp_id}                ← Detalhes da PMP
```

### **✅ Tabelas PMP criadas:**
```
✅ pmps - 0 registros
✅ atividades_pmp - 0 registros  
✅ historico_execucao_pmp - 0 registros
```

### **✅ Funcionalidade PMP:**
- Botão "Gerar PMPs" funcionando
- Agrupamento automático de atividades
- Interface integrada na aba do plano mestre

## 🔍 **TESTE FINAL**

1. **Acessar plano mestre** de um equipamento
2. **Clicar na aba** "Procedimentos de manutenção preventiva"
3. **Clicar em "Gerar PMPs"**
4. **Verificar se PMPs são criadas** sem erro 500

## 📦 **ARQUIVOS NO ZIP**

```
correcao_erro_500_pmp.zip
├── app.py                       ← Import 'os' corrigido
├── routes/pmp.py               ← Blueprint PMP completo
├── models/pmp.py               ← Modelos atualizados
├── static/plano-mestre.html    ← Interface integrada
├── static/js/plano-mestre.js   ← JavaScript PMP
├── create_pmp_tables_final.py  ← Script de tabelas
└── CORREÇÃO_ERRO_500_PMP.md    ← Esta documentação
```

## 🎉 **APÓS A CORREÇÃO**

O sistema PMP estará **100% funcional** com:
- ✅ Erro 500 corrigido
- ✅ Interface integrada
- ✅ Agrupamento automático
- ✅ Múltiplas PMPs por equipamento
- ✅ Códigos únicos (PMP-XX-TagEquipamento)
- ✅ Configuração completa de PMPs

