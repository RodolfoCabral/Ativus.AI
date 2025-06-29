"""
APIs de Teste para Sistema de Ativos
Permite limpar dados e popular com dados de exemplo
"""

from flask import Flask, jsonify, request
from flask_login import login_required, current_user
from models import db
from assets_models import Filial, Setor, Equipamento, Categoria
from datetime import datetime
import os

def register_test_apis(app):
    """Registra as APIs de teste no app Flask"""
    
    @app.route('/api/test/clear-all-assets', methods=['POST'])
    @login_required
    def clear_all_assets():
        """
        Limpa todos os dados de ativos do sistema
        Apenas usuários master podem executar
        """
        try:
            # Verificar se é usuário master
            if current_user.role != 'master':
                return jsonify({
                    'success': False,
                    'message': 'Apenas usuários master podem limpar dados'
                }), 403
            
            # Limpar todas as tabelas na ordem correta (devido às foreign keys)
            db.session.query(Equipamento).delete()
            db.session.query(Setor).delete()
            db.session.query(Filial).delete()
            db.session.query(Categoria).delete()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Todos os dados de ativos foram removidos com sucesso'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Erro ao limpar dados: {str(e)}'
            }), 500
    
    @app.route('/api/test/populate-sample-data', methods=['POST'])
    @login_required
    def populate_sample_data():
        """
        Popula o sistema com dados de exemplo
        Apenas usuários master podem executar
        """
        try:
            # Verificar se é usuário master
            if current_user.role != 'master':
                return jsonify({
                    'success': False,
                    'message': 'Apenas usuários master podem popular dados'
                }), 403
            
            # Dados de exemplo
            sample_data = {
                'filiais': [
                    {
                        'tag': 'F001',
                        'descricao': 'Unidade Olinda',
                        'endereco': 'Rua das Indústrias, 123',
                        'cidade': 'Olinda',
                        'estado': 'PE',
                        'email': 'olinda@ativus.com.br',
                        'telefone': '(81) 3333-4444',
                        'cnpj': '12.345.678/0001-90'
                    },
                    {
                        'tag': 'F002',
                        'descricao': 'Unidade Recife',
                        'endereco': 'Av. Boa Viagem, 456',
                        'cidade': 'Recife',
                        'estado': 'PE',
                        'email': 'recife@ativus.com.br',
                        'telefone': '(81) 3555-6666',
                        'cnpj': '12.345.678/0002-71'
                    },
                    {
                        'tag': 'F003',
                        'descricao': 'Unidade São Paulo',
                        'endereco': 'Rua Paulista, 789',
                        'cidade': 'São Paulo',
                        'estado': 'SP',
                        'email': 'saopaulo@ativus.com.br',
                        'telefone': '(11) 3777-8888',
                        'cnpj': '12.345.678/0003-52'
                    }
                ],
                'setores': [
                    {'tag': 'PM', 'descricao': 'Pré-moldagem', 'filial_tag': 'F001'},
                    {'tag': 'MT', 'descricao': 'Montagem', 'filial_tag': 'F001'},
                    {'tag': 'QC', 'descricao': 'Controle de Qualidade', 'filial_tag': 'F001'},
                    {'tag': 'PR', 'descricao': 'Produção', 'filial_tag': 'F002'},
                    {'tag': 'LG', 'descricao': 'Logística', 'filial_tag': 'F002'},
                    {'tag': 'AD', 'descricao': 'Administrativo', 'filial_tag': 'F003'},
                    {'tag': 'TI', 'descricao': 'Tecnologia da Informação', 'filial_tag': 'F003'}
                ],
                'equipamentos': [
                    {'tag': 'EQP001', 'descricao': 'Máquina de Corte CNC', 'setor_tag': 'PM'},
                    {'tag': 'EQP002', 'descricao': 'Prensa Hidráulica 50T', 'setor_tag': 'PM'},
                    {'tag': 'EQP003', 'descricao': 'Soldadora MIG/MAG', 'setor_tag': 'MT'},
                    {'tag': 'EQP004', 'descricao': 'Ponte Rolante 10T', 'setor_tag': 'MT'},
                    {'tag': 'EQP005', 'descricao': 'Medidor de Rugosidade', 'setor_tag': 'QC'},
                    {'tag': 'EQP006', 'descricao': 'Máquina de Tração Universal', 'setor_tag': 'QC'},
                    {'tag': 'EQP007', 'descricao': 'Linha de Produção A', 'setor_tag': 'PR'},
                    {'tag': 'EQP008', 'descricao': 'Empilhadeira Elétrica', 'setor_tag': 'LG'},
                    {'tag': 'EQP009', 'descricao': 'Servidor Principal', 'setor_tag': 'TI'},
                    {'tag': 'EQP010', 'descricao': 'Switch de Rede 48 Portas', 'setor_tag': 'TI'}
                ],
                'categorias': [
                    {'nome': 'Máquinas de Corte', 'descricao': 'Equipamentos para corte de materiais'},
                    {'nome': 'Equipamentos de Solda', 'descricao': 'Máquinas e equipamentos de soldagem'},
                    {'nome': 'Instrumentos de Medição', 'descricao': 'Equipamentos para controle de qualidade'},
                    {'nome': 'Equipamentos de Movimentação', 'descricao': 'Pontes rolantes, empilhadeiras, etc.'},
                    {'nome': 'Equipamentos de TI', 'descricao': 'Servidores, switches, computadores'},
                    {'nome': 'Linhas de Produção', 'descricao': 'Sistemas completos de produção'}
                ]
            }
            
            # Criar filiais
            filiais_criadas = {}
            for filial_data in sample_data['filiais']:
                filial = Filial(
                    tag=filial_data['tag'],
                    descricao=filial_data['descricao'],
                    endereco=filial_data['endereco'],
                    cidade=filial_data['cidade'],
                    estado=filial_data['estado'],
                    email=filial_data['email'],
                    telefone=filial_data['telefone'],
                    cnpj=filial_data['cnpj'],
                    empresa=current_user.company,
                    usuario_criacao=current_user.email
                )
                db.session.add(filial)
                db.session.flush()  # Para obter o ID
                filiais_criadas[filial_data['tag']] = filial.id
            
            # Criar setores
            setores_criados = {}
            for setor_data in sample_data['setores']:
                filial_id = filiais_criadas[setor_data['filial_tag']]
                setor = Setor(
                    tag=setor_data['tag'],
                    descricao=setor_data['descricao'],
                    filial_id=filial_id,
                    empresa=current_user.company,
                    usuario_criacao=current_user.email
                )
                db.session.add(setor)
                db.session.flush()  # Para obter o ID
                setores_criados[setor_data['tag']] = setor.id
            
            # Criar equipamentos
            for equipamento_data in sample_data['equipamentos']:
                setor_id = setores_criados[equipamento_data['setor_tag']]
                equipamento = Equipamento(
                    tag=equipamento_data['tag'],
                    descricao=equipamento_data['descricao'],
                    setor_id=setor_id,
                    empresa=current_user.company,
                    usuario_criacao=current_user.email
                )
                db.session.add(equipamento)
            
            # Criar categorias
            for categoria_data in sample_data['categorias']:
                categoria = Categoria(
                    nome=categoria_data['nome'],
                    descricao=categoria_data['descricao'],
                    empresa=current_user.company,
                    usuario_criacao=current_user.email
                )
                db.session.add(categoria)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Dados de exemplo criados com sucesso',
                'data': {
                    'filiais': len(sample_data['filiais']),
                    'setores': len(sample_data['setores']),
                    'equipamentos': len(sample_data['equipamentos']),
                    'categorias': len(sample_data['categorias'])
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Erro ao criar dados de exemplo: {str(e)}'
            }), 500
    
    @app.route('/api/test/assets-stats', methods=['GET'])
    @login_required
    def get_assets_stats():
        """
        Retorna estatísticas dos ativos no sistema
        """
        try:
            # Filtrar por empresa se não for master
            if current_user.role == 'master':
                filiais_count = db.session.query(Filial).count()
                setores_count = db.session.query(Setor).count()
                equipamentos_count = db.session.query(Equipamento).count()
                categorias_count = db.session.query(Categoria).count()
            else:
                filiais_count = db.session.query(Filial).filter_by(empresa=current_user.company).count()
                setores_count = db.session.query(Setor).filter_by(empresa=current_user.company).count()
                equipamentos_count = db.session.query(Equipamento).filter_by(empresa=current_user.company).count()
                categorias_count = db.session.query(Categoria).filter_by(empresa=current_user.company).count()
            
            return jsonify({
                'success': True,
                'stats': {
                    'filiais': filiais_count,
                    'setores': setores_count,
                    'equipamentos': equipamentos_count,
                    'categorias': categorias_count
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao obter estatísticas: {str(e)}'
            }), 500
    
    @app.route('/api/test/clear-company-assets', methods=['POST'])
    @login_required
    def clear_company_assets():
        """
        Limpa apenas os dados de ativos da empresa do usuário logado
        Usuários admin e master podem executar
        """
        try:
            # Verificar se é usuário admin ou master
            if current_user.role not in ['admin', 'master']:
                return jsonify({
                    'success': False,
                    'message': 'Apenas usuários admin ou master podem limpar dados'
                }), 403
            
            # Determinar empresa a ser limpa
            empresa = current_user.company
            
            # Limpar dados da empresa na ordem correta
            equipamentos_removidos = db.session.query(Equipamento).filter_by(empresa=empresa).delete()
            setores_removidos = db.session.query(Setor).filter_by(empresa=empresa).delete()
            filiais_removidas = db.session.query(Filial).filter_by(empresa=empresa).delete()
            categorias_removidas = db.session.query(Categoria).filter_by(empresa=empresa).delete()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Dados da empresa {empresa} removidos com sucesso',
                'removed': {
                    'filiais': filiais_removidas,
                    'setores': setores_removidos,
                    'equipamentos': equipamentos_removidos,
                    'categorias': categorias_removidas
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Erro ao limpar dados da empresa: {str(e)}'
            }), 500

    return app

