from flask import Blueprint, request, jsonify, current_app
from models import db
import logging
import traceback

# Tentar importar o modelo correto
try:
    from models.pmp_limpo import PMP
    current_app.logger.info("✅ Importado modelo PMP_LIMPO")
except ImportError:
    try:
        from models.pmp import PMP
        current_app.logger.info("⚠️ Importado modelo PMP antigo")
    except ImportError:
        current_app.logger.error("❌ Nenhum modelo PMP encontrado!")
        PMP = None

pmp_debug_bp = Blueprint('pmp_debug_bp', __name__)

@pmp_debug_bp.route('/api/pmp/<int:pmp_id>/debug-atualizar', methods=['PUT'])
def debug_atualizar_pmp(pmp_id):
    """
    Versão de DEBUG EXTREMO da atualização PMP
    """
    try:
        current_app.logger.info("=" * 60)
        current_app.logger.info(f"🔧 DEBUG EXTREMO - Atualizando PMP {pmp_id}")
        current_app.logger.info("=" * 60)
        
        # 1. Verificar se modelo existe
        if PMP is None:
            current_app.logger.error("❌ Modelo PMP não disponível")
            return jsonify({'success': False, 'message': 'Modelo PMP não disponível'}), 500
        
        current_app.logger.info(f"✅ Modelo PMP disponível: {PMP}")
        
        # 2. Verificar dados recebidos
        data = request.get_json()
        current_app.logger.info(f"📦 Dados recebidos: {data}")
        current_app.logger.info(f"📦 Tipo dos dados: {type(data)}")
        
        if not data:
            current_app.logger.error("❌ Nenhum dado recebido")
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # 3. Buscar PMP no banco
        current_app.logger.info(f"🔍 Buscando PMP {pmp_id} no banco...")
        
        try:
            pmp = PMP.query.get(pmp_id)
            current_app.logger.info(f"📋 Resultado da busca: {pmp}")
        except Exception as e:
            current_app.logger.error(f"❌ Erro na busca: {e}")
            current_app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'message': f'Erro na busca: {str(e)}'}), 500
        
        if not pmp:
            current_app.logger.error(f"❌ PMP {pmp_id} não encontrada")
            return jsonify({'success': False, 'message': 'PMP não encontrada'}), 404
        
        current_app.logger.info(f"✅ PMP encontrada: {pmp.codigo}")
        
        # 4. Mostrar valores atuais
        current_app.logger.info("📊 VALORES ATUAIS:")
        current_app.logger.info(f"   - num_pessoas: {pmp.num_pessoas} (tipo: {type(pmp.num_pessoas)})")
        current_app.logger.info(f"   - tempo_pessoa: {pmp.tempo_pessoa} (tipo: {type(pmp.tempo_pessoa)})")
        current_app.logger.info(f"   - dias_antecipacao: {pmp.dias_antecipacao} (tipo: {type(pmp.dias_antecipacao)})")
        current_app.logger.info(f"   - forma_impressao: {pmp.forma_impressao} (tipo: {type(pmp.forma_impressao)})")
        
        # 5. Atualizar campos um por um
        alteracoes = []
        
        if 'num_pessoas' in data:
            valor_antigo = pmp.num_pessoas
            novo_valor = int(data['num_pessoas'])
            pmp.num_pessoas = novo_valor
            alteracoes.append(f"num_pessoas: {valor_antigo} → {novo_valor}")
            current_app.logger.info(f"🔄 num_pessoas: {valor_antigo} → {novo_valor}")
        
        if 'tempo_pessoa' in data:
            valor_antigo = pmp.tempo_pessoa
            novo_valor = float(data['tempo_pessoa'])
            pmp.tempo_pessoa = novo_valor
            alteracoes.append(f"tempo_pessoa: {valor_antigo} → {novo_valor}")
            current_app.logger.info(f"🔄 tempo_pessoa: {valor_antigo} → {novo_valor}")
        
        if 'dias_antecipacao' in data:
            valor_antigo = pmp.dias_antecipacao
            novo_valor = int(data['dias_antecipacao'])
            pmp.dias_antecipacao = novo_valor
            alteracoes.append(f"dias_antecipacao: {valor_antigo} → {novo_valor}")
            current_app.logger.info(f"🔄 dias_antecipacao: {valor_antigo} → {novo_valor}")
        
        if 'forma_impressao' in data:
            valor_antigo = pmp.forma_impressao
            novo_valor = str(data['forma_impressao'])
            pmp.forma_impressao = novo_valor
            alteracoes.append(f"forma_impressao: {valor_antigo} → {novo_valor}")
            current_app.logger.info(f"🔄 forma_impressao: {valor_antigo} → {novo_valor}")
        
        current_app.logger.info(f"📝 Total de alterações: {len(alteracoes)}")
        
        # 6. Mostrar valores após alteração (antes do commit)
        current_app.logger.info("📊 VALORES APÓS ALTERAÇÃO (ANTES DO COMMIT):")
        current_app.logger.info(f"   - num_pessoas: {pmp.num_pessoas}")
        current_app.logger.info(f"   - tempo_pessoa: {pmp.tempo_pessoa}")
        current_app.logger.info(f"   - dias_antecipacao: {pmp.dias_antecipacao}")
        current_app.logger.info(f"   - forma_impressao: {pmp.forma_impressao}")
        
        # 7. Tentar commit
        current_app.logger.info("💾 INICIANDO PROCESSO DE COMMIT...")
        
        try:
            # Adicionar à sessão
            current_app.logger.info("📌 Adicionando PMP à sessão...")
            db.session.add(pmp)
            current_app.logger.info("✅ PMP adicionada à sessão")
            
            # Flush
            current_app.logger.info("🔄 Executando flush...")
            db.session.flush()
            current_app.logger.info("✅ Flush executado")
            
            # Commit
            current_app.logger.info("💾 Executando commit...")
            db.session.commit()
            current_app.logger.info("✅ Commit executado com sucesso!")
            
        except Exception as commit_error:
            current_app.logger.error(f"❌ ERRO NO COMMIT: {commit_error}")
            current_app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            db.session.rollback()
            current_app.logger.info("🔄 Rollback executado")
            return jsonify({
                'success': False, 
                'message': f'Erro no commit: {str(commit_error)}'
            }), 500
        
        # 8. Verificar se foi realmente salvo
        current_app.logger.info("🔍 VERIFICAÇÃO PÓS-COMMIT...")
        
        try:
            pmp_verificacao = PMP.query.get(pmp_id)
            current_app.logger.info("📊 VALORES PÓS-COMMIT:")
            current_app.logger.info(f"   - num_pessoas: {pmp_verificacao.num_pessoas}")
            current_app.logger.info(f"   - tempo_pessoa: {pmp_verificacao.tempo_pessoa}")
            current_app.logger.info(f"   - dias_antecipacao: {pmp_verificacao.dias_antecipacao}")
            current_app.logger.info(f"   - forma_impressao: {pmp_verificacao.forma_impressao}")
            
            # Verificar se mudou
            mudou = False
            if 'num_pessoas' in data and pmp_verificacao.num_pessoas == int(data['num_pessoas']):
                mudou = True
            if 'tempo_pessoa' in data and pmp_verificacao.tempo_pessoa == float(data['tempo_pessoa']):
                mudou = True
                
            if mudou:
                current_app.logger.info("🎉 SUCESSO! Valores foram alterados no banco!")
            else:
                current_app.logger.error("❌ FALHA! Valores não foram alterados no banco!")
            
        except Exception as verify_error:
            current_app.logger.error(f"❌ Erro na verificação: {verify_error}")
        
        current_app.logger.info("=" * 60)
        current_app.logger.info("🎯 DEBUG EXTREMO CONCLUÍDO")
        current_app.logger.info("=" * 60)
        
        return jsonify({
            'success': True,
            'message': 'Debug concluído - verificar logs',
            'alteracoes': alteracoes,
            'pmp': pmp.to_dict() if hasattr(pmp, 'to_dict') else str(pmp)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERRO GERAL: {e}")
        current_app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Erro geral: {str(e)}'
        }), 500

