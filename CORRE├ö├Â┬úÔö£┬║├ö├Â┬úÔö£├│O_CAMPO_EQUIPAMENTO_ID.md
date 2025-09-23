# 🔧 CORREÇÃO DO CAMPO EQUIPAMENTO_ID - PMP

## 🚨 **PROBLEMA IDENTIFICADO**

```
AttributeError: type object 'AtividadePlanoMestre' has no attribute 'equipamento_id'
```

**Causa:** O modelo `AtividadePlanoMestre` não tem campo `equipamento_id` diretamente.

## 📋 **ESTRUTURA CORRETA DO BANCO**

```
Equipamento (id=232, tag="F01-EXT-BB01")
    ↓
PlanoMestre (equipamento_id=232)
    ↓  
AtividadePlanoMestre (plano_mestre_id=X)
```

**Relacionamento:**
- `AtividadePlanoMestre` → `plano_mestre_id` → `PlanoMestre` → `equipamento_id`

## ✅ **CORREÇÃO APLICADA**

### **Antes (INCORRETO):**
```python
# ❌ Tentava buscar diretamente por equipamento_id
atividades = AtividadePlanoMestre.query.filter_by(equipamento_id=equipamento_id).all()
```

### **Depois (CORRETO):**
```python
# ✅ Busca primeiro o plano mestre, depois as atividades
plano_mestre = PlanoMestre.query.filter_by(equipamento_id=equipamento_id).first()
atividades = AtividadePlanoMestre.query.filter_by(plano_mestre_id=plano_mestre.id).all()
```

## 🔧 **ARQUIVO CORRIGIDO**

- **`routes/pmp.py`** - Função `gerar_pmps()` corrigida

## 🚀 **INSTRUÇÕES DE DEPLOY**

### **1. Substituir arquivo:**
```bash
cp routes/pmp.py "SaaS Ativus/routes/"
```

### **2. Deploy no Heroku:**
```bash
git add routes/pmp.py
git commit -m "Correção campo equipamento_id na geração de PMPs"
git push heroku main
```

### **3. Testar:**
- Acessar plano mestre do equipamento
- Clicar na aba "Procedimentos de manutenção preventiva"  
- Clicar em "Gerar PMPs"
- **Deve funcionar sem erro 500**

## 🎯 **RESULTADO ESPERADO**

Após a correção:
- ✅ **Sem erro 500** - API funcionando
- ✅ **PMPs geradas** - Agrupamento correto
- ✅ **Interface funcionando** - Sidebar e formulário

## 📦 **ARQUIVO NO ZIP**

```
correcao_campo_equipamento_id.zip
├── routes/pmp.py                    ← Arquivo corrigido
└── CORREÇÃO_CAMPO_EQUIPAMENTO_ID.md ← Esta documentação
```

