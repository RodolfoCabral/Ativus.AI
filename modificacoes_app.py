# MODIFICAÇÕES NECESSÁRIAS NO SEU ARQUIVO app.py
# Adicione estas linhas no final do seu arquivo app.py, antes do if __name__ == "__main__":

# ============================================================================
# INÍCIO DAS MODIFICAÇÕES - Funcionalidade de Atividades de OS
# ============================================================================

# 1. Importar o novo modelo (adicionar no topo do arquivo, junto com outros imports)
from models.atividade_os import AtividadeOS

# 2. Importar e registrar os novos blueprints (adicionar no final, antes do if __name__)
try:
    from routes.atividades_os import atividades_os_bp
    app.register_blueprint(atividades_os_bp)
    logger.info("✅ Blueprint 'atividades_os' registrado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar blueprint atividades_os: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao registrar blueprint atividades_os: {e}")

# ============================================================================
# FIM DAS MODIFICAÇÕES
# ============================================================================

# Exemplo de como deve ficar o final do seu app.py:
"""
# ... seu código existente ...

# Importar novos modelos
from models.atividade_os import AtividadeOS

# Registrar novos blueprints
try:
    from routes.atividades_os import atividades_os_bp
    app.register_blueprint(atividades_os_bp)
    logger.info("✅ Blueprint 'atividades_os' registrado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar blueprint atividades_os: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao registrar blueprint atividades_os: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
"""
