#!/usr/bin/env python3
"""
Script para testar conexão real com o banco de dados
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def testar_conexao_direta():
    """Testa conexão direta com PostgreSQL"""
    
    print("🔗 TESTANDO CONEXÃO DIRETA COM BANCO")
    print("=" * 50)
    
    # Tentar pegar URL do banco das variáveis de ambiente
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
        print("💡 Defina a variável DATABASE_URL")
        return False
    
    try:
        # Parse da URL do banco
        url = urlparse(database_url)
        
        print(f"🏢 Host: {url.hostname}")
        print(f"🗄️ Database: {url.path[1:]}")
        print(f"👤 User: {url.username}")
        
        # Conectar ao banco
        conn = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            port=url.port or 5432
        )
        
        cursor = conn.cursor()
        
        print("✅ CONEXÃO ESTABELECIDA!")
        
        # Listar todas as tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        print(f"\n📋 TABELAS ENCONTRADAS ({len(tabelas)}):")
        
        tabelas_user = []
        for (tabela,) in tabelas:
            print(f"  - {tabela}")
            if 'user' in tabela.lower():
                tabelas_user.append(tabela)
        
        print(f"\n👤 TABELAS DE USUÁRIOS: {tabelas_user}")
        
        # Testar cada tabela de usuário
        for tabela in tabelas_user:
            print(f"\n🔍 TESTANDO TABELA: {tabela}")
            
            try:
                # Verificar colunas
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{tabela}'
                    ORDER BY ordinal_position
                """)
                
                colunas = cursor.fetchall()
                print(f"📊 Colunas:")
                for coluna, tipo in colunas:
                    print(f"  - {coluna} ({tipo})")
                
                # Verificar se tem coluna company
                colunas_nomes = [col[0] for col in colunas]
                if 'company' in colunas_nomes:
                    print("✅ Coluna 'company' encontrada!")
                    
                    # Contar registros
                    cursor.execute(f'SELECT COUNT(*) FROM "{tabela}"')
                    total = cursor.fetchone()[0]
                    print(f"📊 Total de registros: {total}")
                    
                    # Mostrar primeiros registros
                    cursor.execute(f'SELECT * FROM "{tabela}" LIMIT 3')
                    registros = cursor.fetchall()
                    
                    print(f"📄 Primeiros registros:")
                    for i, registro in enumerate(registros, 1):
                        dados = dict(zip(colunas_nomes, registro))
                        print(f"  {i}. {dados}")
                    
                    # Testar query específica
                    print(f"\n🧪 TESTANDO QUERY ESPECÍFICA:")
                    
                    # Buscar usuário ID 1
                    cursor.execute(f'SELECT id, name, email, company FROM "{tabela}" WHERE id = 1')
                    usuario = cursor.fetchone()
                    
                    if usuario:
                        user_id, name, email, company = usuario
                        print(f"👤 Usuário ID 1: {name} ({email}) - Empresa: {company}")
                        
                        # Buscar outros usuários da mesma empresa
                        cursor.execute(f'''
                            SELECT id, name, email, cargo 
                            FROM "{tabela}" 
                            WHERE company = %s AND id != 1
                            ORDER BY name
                        ''', (company,))
                        
                        colegas = cursor.fetchall()
                        print(f"👥 Colegas da empresa {company}:")
                        for colega in colegas:
                            print(f"  - {colega}")
                        
                        return True
                    else:
                        print("❌ Usuário ID 1 não encontrado")
                else:
                    print("❌ Coluna 'company' não encontrada")
                    
            except Exception as e:
                print(f"❌ Erro ao testar tabela {tabela}: {e}")
        
        cursor.close()
        conn.close()
        
        return False
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def gerar_api_corrigida():
    """Gera versão corrigida da API baseada nos achados"""
    
    print("\n🔧 GERANDO API CORRIGIDA")
    print("=" * 30)
    
    api_code = '''
@pmp_limpo_bp.route('/api/usuarios/empresa', methods=['GET'])
def buscar_usuarios_empresa():
    """
    Busca usuários reais da mesma empresa - VERSÃO CORRIGIDA
    """
    try:
        current_app.logger.info("🔍 Buscando usuários da empresa - VERSÃO CORRIGIDA")
        
        # Pegar usuário logado (ajustar conforme sua autenticação)
        usuario_logado_id = 1  # FIXME: Pegar da sessão real
        
        from sqlalchemy import text
        
        # CONEXÃO DIRETA - Testar primeiro
        try:
            # Verificar se consegue conectar
            result_test = db.session.execute(text("SELECT 1"))
            current_app.logger.info("✅ Conexão com banco OK")
        except Exception as e:
            current_app.logger.error(f"❌ Erro de conexão: {e}")
            raise Exception("Erro de conexão com banco")
        
        # BUSCAR TABELAS DISPONÍVEIS
        try:
            result_tables = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name ILIKE '%user%'
            """))
            
            tabelas_disponiveis = [row[0] for row in result_tables.fetchall()]
            current_app.logger.info(f"📋 Tabelas de usuários encontradas: {tabelas_disponiveis}")
            
        except Exception as e:
            current_app.logger.error(f"❌ Erro ao listar tabelas: {e}")
            tabelas_disponiveis = ['user', 'users']
        
        # TESTAR CADA TABELA
        for nome_tabela in tabelas_disponiveis:
            try:
                current_app.logger.info(f"🔍 Testando tabela: {nome_tabela}")
                
                # Verificar se usuário existe
                query_usuario = text(f'''
                    SELECT id, name, email, company 
                    FROM "{nome_tabela}" 
                    WHERE id = :user_id
                ''')
                
                result_usuario = db.session.execute(query_usuario, {'user_id': usuario_logado_id})
                usuario_row = result_usuario.fetchone()
                
                if not usuario_row:
                    current_app.logger.info(f"⚠️ Usuário {usuario_logado_id} não encontrado em {nome_tabela}")
                    continue
                
                user_id, name, email, company_id = usuario_row
                current_app.logger.info(f"👤 Usuário encontrado: {name} ({email}) - Empresa: {company_id}")
                
                # Buscar colegas da mesma empresa
                query_colegas = text(f'''
                    SELECT id, name, email, cargo
                    FROM "{nome_tabela}" 
                    WHERE company = :company_id 
                    AND id != :user_id
                    ORDER BY name
                ''')
                
                result_colegas = db.session.execute(query_colegas, {
                    'company_id': company_id,
                    'user_id': usuario_logado_id
                })
                
                colegas = result_colegas.fetchall()
                
                # Converter para formato esperado
                usuarios_lista = []
                for colega in colegas:
                    usuarios_lista.append({
                        'id': colega.id,
                        'nome': colega.name,
                        'email': colega.email,
                        'cargo': colega.cargo or 'Não informado',
                        'status': 'ativo'
                    })
                
                current_app.logger.info(f"✅ SUCESSO! Encontrados {len(usuarios_lista)} usuários da empresa {company_id}")
                
                # Log dos usuários encontrados
                for usuario in usuarios_lista:
                    current_app.logger.info(f"  - {usuario['nome']} ({usuario['email']})")
                
                return jsonify({
                    'success': True,
                    'usuarios': usuarios_lista,
                    'total': len(usuarios_lista),
                    'empresa_id': company_id,
                    'usuario_logado': {'id': user_id, 'nome': name, 'email': email},
                    'tabela_usada': nome_tabela,
                    'fonte': 'banco_real',
                    'timestamp': datetime.now().isoformat()
                }), 200
                
            except Exception as e:
                current_app.logger.error(f"❌ Erro na tabela {nome_tabela}: {e}")
                continue
        
        # Se chegou aqui, nenhuma tabela funcionou
        raise Exception("Nenhuma tabela de usuários acessível")
        
    except Exception as e:
        current_app.logger.error(f"❌ ERRO FINAL: {e}", exc_info=True)
        
        # DADOS MOCK COMO ÚLTIMO RECURSO
        usuarios_mock = [
            {'id': 999, 'nome': 'DADOS MOCK - ERRO NO BANCO', 'email': 'mock@erro.com', 'cargo': 'Erro', 'status': 'mock'}
        ]
        
        return jsonify({
            'success': True,
            'usuarios': usuarios_mock,
            'total': len(usuarios_mock),
            'mock': True,
            'erro': str(e),
            'instrucoes': 'Verifique conexão com banco e estrutura da tabela user'
        }), 200
'''
    
    with open('/home/ubuntu/api_usuarios_corrigida.py', 'w') as f:
        f.write(api_code)
    
    print("✅ API corrigida salva em: api_usuarios_corrigida.py")

if __name__ == "__main__":
    # Testar conexão
    sucesso = testar_conexao_direta()
    
    # Gerar API corrigida
    gerar_api_corrigida()
    
    if sucesso:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("💡 Use a API corrigida gerada")
    else:
        print("\n⚠️ PROBLEMAS ENCONTRADOS")
        print("💡 Verifique DATABASE_URL e estrutura do banco")

