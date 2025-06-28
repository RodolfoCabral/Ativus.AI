# APIs simplificadas para ativos - para adicionar ao app.py

@app.route('/api/filiais', methods=['GET'])
@login_required
def api_get_filiais():
    """API simplificada para filiais"""
    try:
        # Simular dados para teste
        filiais_mock = [
            {
                'id': 1,
                'tag': 'F01',
                'descricao': 'Unidade olinda',
                'endereco': 'Rua Principal, 123',
                'cidade': 'Olinda',
                'estado': 'PE',
                'email': 'filial@empresa.com',
                'telefone': '(81) 99999-9999',
                'cnpj': '12.345.678/0001-90',
                'empresa': current_user.company,
                'data_criacao': '2024-06-26T10:00:00',
                'usuario_criacao': current_user.email
            }
        ]
        
        return jsonify({
            'success': True,
            'filiais': filiais_mock
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/setores', methods=['GET'])
@login_required
def api_get_setores():
    """API simplificada para setores"""
    try:
        setores_mock = [
            {
                'id': 1,
                'tag': 'PM',
                'descricao': 'Pré-moldagem',
                'filial_id': 1,
                'empresa': current_user.company,
                'data_criacao': '2024-06-26T10:00:00',
                'usuario_criacao': current_user.email
            }
        ]
        
        return jsonify({
            'success': True,
            'setores': setores_mock
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/equipamentos', methods=['GET'])
@login_required
def api_get_equipamentos():
    """API simplificada para equipamentos"""
    try:
        equipamentos_mock = [
            {
                'id': 1,
                'tag': 'EQP001',
                'descricao': 'Máquina de Corte',
                'setor_id': 1,
                'empresa': current_user.company,
                'data_criacao': '2024-06-26T10:00:00',
                'usuario_criacao': current_user.email
            }
        ]
        
        return jsonify({
            'success': True,
            'equipamentos': equipamentos_mock
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

