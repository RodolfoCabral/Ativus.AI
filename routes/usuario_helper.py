"""
Helper para buscar informações de usuários
"""

from flask import current_app

def buscar_nome_usuario_por_id(user_id):
    """
    Busca o nome do usuário pelo ID com múltiplos fallbacks
    
    Args:
        user_id: ID do usuário (pode ser string ou int)
    
    Returns:
        str: Nome do usuário ou fallback se não encontrado
    """
    try:
        # Se user_id é None ou vazio, retornar None
        if not user_id:
            return None
        
        # Converter para int se necessário
        original_user_id = user_id
        if isinstance(user_id, str):
            # Se já parece ser um nome (contém letras), retornar como está
            if any(c.isalpha() for c in user_id):
                current_app.logger.info(f"🔍 user_id '{user_id}' contém letras, assumindo que é nome")
                return user_id
            
            try:
                user_id = int(user_id)
            except ValueError:
                current_app.logger.warning(f"⚠️ user_id '{user_id}' não é numérico válido")
                return f"Usuario_{original_user_id}"
        
        # Tentar importar modelo de usuário
        try:
            from assets_models import User
        except ImportError:
            current_app.logger.warning("⚠️ Modelo User não disponível, usando fallback")
            return f"Usuario_{user_id}"
        
        # Buscar usuário pelo ID
        usuario = User.query.get(user_id)
        
        if usuario:
            # Tentar diferentes campos de nome em ordem de prioridade
            campos_nome = ['name', 'username', 'nome', 'login', 'user_name']
            
            for campo in campos_nome:
                if hasattr(usuario, campo):
                    valor = getattr(usuario, campo)
                    if valor and isinstance(valor, str) and valor.strip():
                        current_app.logger.info(f"✅ Usuário ID {user_id} encontrado: {valor} (campo: {campo})")
                        return valor.strip()
            
            # Se não encontrou nome nos campos principais, tentar email
            if hasattr(usuario, 'email') and usuario.email:
                nome_email = usuario.email.split('@')[0]
                current_app.logger.info(f"✅ Usuário ID {user_id} usando email: {nome_email}")
                return nome_email
            
            # Se tem ID mas nenhum nome válido
            current_app.logger.warning(f"⚠️ Usuário ID {user_id} encontrado mas sem nome válido")
            return f"Usuario_{user_id}"
        else:
            current_app.logger.warning(f"⚠️ Usuário ID {user_id} não encontrado no banco")
            return f"Usuario_{user_id}"
            
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao buscar usuário {original_user_id}: {e}")
        # Fallback seguro
        return f"Usuario_{original_user_id}"

def buscar_usuarios_por_ids(user_ids):
    """
    Busca nomes de múltiplos usuários pelos IDs
    
    Args:
        user_ids: Lista de IDs de usuários
    
    Returns:
        list: Lista de nomes de usuários
    """
    if not user_ids:
        return []
    
    nomes = []
    for user_id in user_ids:
        nome = buscar_nome_usuario_por_id(user_id)
        if nome:
            nomes.append(nome)
    
    return nomes

def validar_usuario_existe(user_id):
    """
    Valida se um usuário existe
    
    Args:
        user_id: ID do usuário
    
    Returns:
        bool: True se existe, False caso contrário
    """
    try:
        from assets_models import User
        
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return False
        
        usuario = User.query.get(user_id)
        return usuario is not None
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao validar usuário {user_id}: {e}")
        return False

def listar_usuarios_ativos():
    """
    Lista todos os usuários ativos do sistema
    
    Returns:
        list: Lista de dicionários com id, nome dos usuários
    """
    try:
        from assets_models import User
        
        usuarios = User.query.all()
        resultado = []
        
        for usuario in usuarios:
            nome = None
            if hasattr(usuario, 'name') and usuario.name:
                nome = usuario.name
            elif hasattr(usuario, 'username') and usuario.username:
                nome = usuario.username
            elif hasattr(usuario, 'nome') and usuario.nome:
                nome = usuario.nome
            
            if nome:
                resultado.append({
                    'id': usuario.id,
                    'nome': nome
                })
        
        current_app.logger.info(f"📊 {len(resultado)} usuários ativos encontrados")
        return resultado
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao listar usuários: {e}")
        return []
