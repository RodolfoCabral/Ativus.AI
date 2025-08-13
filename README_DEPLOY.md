# 🚀 SaaS Ativus - Instruções de Deploy

## 📋 Problemas Corrigidos

Esta versão corrige os seguintes problemas identificados no diagnóstico:

- ✅ **Erro de importação do `db`** - `models/__init__.py` agora exporta corretamente o objeto `db`
- ✅ **Blueprint não registrado** - `plano_mestre_bp` agora é registrado automaticamente
- ✅ **Configuração centralizada** - Novo arquivo `config.py` para gerenciar configurações
- ✅ **Logging melhorado** - Sistema de logs mais robusto
- ✅ **Inicialização automática** - Script para criar tabelas automaticamente

## 🗄️ Como Fazer Deploy no Heroku

### 1. **Upload dos Arquivos**
```bash
# Fazer upload de todos os arquivos para seu repositório Git
git add .
git commit -m "Aplicação SaaS Ativus corrigida"
git push heroku main
```

### 2. **Configurar Variáveis de Ambiente**
No painel do Heroku, configure as seguintes variáveis:

```bash
# Obrigatórias
DATABASE_URL=sua_url_do_postgresql
SECRET_KEY=sua_chave_secreta_aqui

# Opcionais
SENDGRID_API_KEY=sua_api_key_sendgrid
FLASK_CONFIG=production
```

### 3. **Inicializar Banco de Dados**
Após o deploy, execute:

```bash
heroku run python init_database.py -a seu-app-name
```

**OU** use o script de criação de tabelas:

```bash
heroku run python create_tables.py -a seu-app-name
```

### 4. **Verificar se Funcionou**
```bash
# Ver logs
heroku logs --tail -a seu-app-name

# Testar aplicação
curl https://seu-app-name.herokuapp.com/
```

## 🔧 Comandos Úteis

### **Verificar Status da Aplicação**
```bash
heroku ps -a seu-app-name
```

### **Acessar Console Python**
```bash
heroku run python -a seu-app-name
```

### **Ver Variáveis de Ambiente**
```bash
heroku config -a seu-app-name
```

### **Reiniciar Aplicação**
```bash
heroku restart -a seu-app-name
```

## 🗄️ Estrutura do Banco de Dados

As seguintes tabelas serão criadas automaticamente:

- **`users`** - Usuários do sistema
- **`planos_mestre`** - Planos mestre por equipamento
- **`atividades_plano_mestre`** - Atividades de cada plano
- **`historico_execucao_plano`** - Histórico de execuções

## 🚨 Solução de Problemas

### **Erro H27 (Client Request Interrupted)**
```bash
# Verificar logs detalhados
heroku logs --tail -a seu-app-name

# Executar diagnóstico
heroku run python debug_startup.py -a seu-app-name
```

### **Erro 404 nas APIs**
```bash
# Verificar se blueprints foram registrados
heroku run python verificar_blueprints.py -a seu-app-name

# Corrigir automaticamente
heroku run python corrigir_blueprints.py -a seu-app-name
```

### **Erro de Banco de Dados**
```bash
# Verificar conexão
heroku run python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    print('Conexão OK:', db.engine.execute('SELECT 1').fetchone())
" -a seu-app-name
```

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs** com `heroku logs --tail`
2. **Executar diagnóstico** com `debug_startup.py`
3. **Verificar variáveis** de ambiente
4. **Recriar tabelas** se necessário

## 🎯 Funcionalidades Incluídas

- ✅ Sistema de login/logout
- ✅ Dashboard principal
- ✅ Gestão de ativos
- ✅ Plano de manutenção
- ✅ **Plano Mestre** (NOVO)
- ✅ Scanner QR
- ✅ Lista de QR Codes
- ✅ Relatórios
- ✅ APIs completas

**A aplicação está pronta para produção!** 🎉

