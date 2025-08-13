import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

class Config:
    """Configuração base da aplicação"""
    
    # Chave secreta para sessões e CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_testing_change_in_production')
    
    # Configuração do banco de dados
    @staticmethod
    def get_database_url():
        """Obtém a URL do banco de dados com fallbacks apropriados"""
        
        # Priorizar a variável HEROKU_POSTGRESQL_NAVY_URL fornecida pelo usuário
        database_url = os.environ.get('HEROKU_POSTGRESQL_NAVY_URL')
        
        # Fallback para DATABASE_URL se HEROKU_POSTGRESQL_NAVY_URL não estiver disponível
        if not database_url:
            database_url = os.environ.get('DATABASE_URL')
        
        # Valor padrão para desenvolvimento local
        if not database_url:
            database_url = 'postgresql://postgres:postgres@localhost:5432/ativus'
        
        # Corrigir prefixo da URL se necessário (Heroku usa postgres://, SQLAlchemy requer postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        return database_url
    
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração do SendGrid
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    
    # Configuração de debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    @classmethod
    def init_app(cls, app):
        """Inicializar configurações específicas da aplicação"""
        pass

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

