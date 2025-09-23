# Instruções Completas - Funcionalidade de Atividades de OS

## 📋 Visão Geral

Esta implementação adiciona a funcionalidade de **Lista de Execução** às Ordens de Serviço geradas a partir de PMPs. Quando uma OS é criada a partir de um PMP, as atividades do PMP são automaticamente copiadas para a OS, permitindo que o técnico avalie cada item como:

- ✅ **Conforme**
- ❌ **Não Conforme** 
- ➖ **Não Aplicável**
- ⏳ **Pendente**

## 🗂️ Estrutura dos Arquivos

```
SaaS Ativus/
├── models/
│   └── atividade_os.py                 # Novo modelo para atividades da OS
├── routes/
│   └── atividades_os.py               # Novas rotas da API
├── static/js/
│   └── atividades-os.js               # JavaScript para interface
├── criar_tabela_atividades_os.py      # Script para criar tabela no Heroku
├── modificacoes_app.py                # Código para adicionar ao app.py
└── modificacoes_programacao_js.js     # Código para adicionar ao programacao.js
```

## 🚀 Passo a Passo para Implementação

### 1. Criar a Tabela no Banco de Dados (Heroku)

Execute este comando no terminal:

```bash
heroku run python criar_tabela_atividades_os.py --app SEU-APP-NAME
```

**Substitua `SEU-APP-NAME` pelo nome do seu app no Heroku.**

### 2. Adicionar os Novos Arquivos ao Projeto

Copie os arquivos para as respectivas pastas:

- `models/atividade_os.py` → pasta `models/` do seu projeto
- `routes/atividades_os.py` → pasta `routes/` do seu projeto  
- `static/js/atividades-os.js` → pasta `static/js/` do seu projeto

### 3. Modificar o arquivo `app.py`

Adicione estas linhas no final do seu `app.py`, **antes** do `if __name__ == "__main__"`:

```python
# Importar novo modelo
from models.atividade_os import AtividadeOS

# Registrar novo blueprint
try:
    from routes.atividades_os import atividades_os_bp
    app.register_blueprint(atividades_os_bp)
    logger.info("✅ Blueprint 'atividades_os' registrado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar blueprint atividades_os: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao registrar blueprint atividades_os: {e}")
```

### 4. Modificar a página `programacao.html`

Adicione esta linha no final da seção de scripts:

```html
<script src="{{ url_for('static', filename='js/atividades-os.js') }}"></script>
```

### 5. Modificar o arquivo `programacao.js`

Adicione esta função no final do arquivo:

```javascript
function adicionarBotaoAtividades(chamadoElement, chamadoData) {
    if (chamadoData.pmp_id) {
        const pmpBadge = document.createElement('span');
        pmpBadge.className = 'badge bg-info ms-2';
        pmpBadge.textContent = 'PMP';
        
        const btnAtividades = document.createElement('button');
        btnAtividades.className = 'btn btn-sm btn-outline-primary ms-2';
        btnAtividades.innerHTML = '<i class="fas fa-list-check"></i>';
        btnAtividades.title = 'Ver Lista de Execução';
        btnAtividades.onclick = (e) => {
            e.stopPropagation();
            abrirModalAtividades(chamadoData.id);
        };
        
        const headerElement = chamadoElement.querySelector('.chamado-header') || chamadoElement.querySelector('.os-header');
        if (headerElement) {
            headerElement.appendChild(pmpBadge);
            headerElement.appendChild(btnAtividades);
        }
    }
}
```

E modifique sua função de renderização de OS para incluir:

```javascript
// No final da função que renderiza as OS, adicione:
adicionarBotaoAtividades(osElement, osData);
```

### 6. Criar Atividades para PMPs Existentes

Para que a funcionalidade funcione, você precisa ter atividades cadastradas nos PMPs. Se ainda não tem, você pode criar um script para popular com dados de exemplo ou usar a interface administrativa.

## 🧪 Como Testar

1. **Verificar Tabela**: Confirme que a tabela foi criada executando o script no Heroku
2. **Deploy**: Faça o deploy das modificações para o Heroku
3. **Testar Interface**: 
   - Acesse a página de programação
   - Procure por OS que foram geradas a partir de PMPs (devem ter um badge "PMP")
   - Clique no botão com ícone de lista para abrir o modal
   - Teste a alteração de status e observações

## 🔧 APIs Disponíveis

### Listar Atividades de uma OS
```
GET /api/os/{os_id}/atividades
```

### Avaliar uma Atividade
```
PUT /api/os/atividades/{atividade_id}/avaliar
Content-Type: application/json

{
    "status": "conforme",
    "observacao": "Executado conforme procedimento"
}
```

## 🎯 Funcionalidades Implementadas

- ✅ Modelo de dados para atividades de OS
- ✅ API para listar atividades de uma OS
- ✅ API para avaliar atividades (status + observação)
- ✅ Interface modal para visualizar e avaliar atividades
- ✅ Salvamento automático das avaliações
- ✅ Indicadores visuais de status das atividades
- ✅ Integração com sistema de programação existente

## 🆘 Solução de Problemas

**Erro ao criar tabela**: Verifique se o comando do Heroku está correto e se você tem permissões

**Modal não abre**: Verifique se o JavaScript foi incluído na página e se não há erros no console

**Atividades não aparecem**: Verifique se a OS foi gerada a partir de um PMP que tem atividades cadastradas

**Erro 404 na API**: Verifique se o blueprint foi registrado corretamente no app.py

## 📞 Suporte

Se tiver dúvidas ou problemas durante a implementação, me informe qual erro específico está ocorrendo e em qual etapa.
