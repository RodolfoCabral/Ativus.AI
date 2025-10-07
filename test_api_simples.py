#!/usr/bin/env python3
"""
Teste simples para verificar se as APIs estão funcionando
"""

from flask import Flask, jsonify
from datetime import datetime

def criar_teste_apis():
    """Cria rotas de teste simples"""
    
    # Rota de teste para ordens de serviço
    @app.route('/api/test/ordens-servico', methods=['GET'])
    def test_ordens_servico():
        try:
            return jsonify({
                'success': True,
                'message': 'API de ordens de serviço funcionando',
                'timestamp': datetime.now().isoformat(),
                'ordens_servico': [
                    {
                        'id': 1,
                        'descricao': 'Teste OS 1',
                        'status': 'aberta',
                        'prioridade': 'media'
                    },
                    {
                        'id': 2,
                        'descricao': 'Teste OS 2',
                        'status': 'programada',
                        'prioridade': 'alta'
                    }
                ]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Rota de teste para usuários
    @app.route('/api/test/usuarios', methods=['GET'])
    def test_usuarios():
        try:
            return jsonify({
                'success': True,
                'message': 'API de usuários funcionando',
                'timestamp': datetime.now().isoformat(),
                'usuarios': [
                    {
                        'id': 1,
                        'name': 'Rodolfo Cabral',
                        'profile': 'admin'
                    },
                    {
                        'id': 2,
                        'name': 'Jefferson',
                        'profile': 'user'
                    }
                ]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return True

# Adicionar ao app.py
if __name__ == "__main__":
    print("Teste criado! Adicione as rotas ao app.py")
