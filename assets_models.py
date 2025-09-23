from sqlalchemy import func
from models import db
from datetime import datetime

class Filial(db.Model):
    __tablename__ = 'filiais'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com setores
    setores = db.relationship('Setor', backref='filial_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'email': self.email,
            'telefone': self.telefone,
            'cnpj': self.cnpj,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Setor(db.Model):
    __tablename__ = 'setores'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com equipamentos
    equipamentos = db.relationship('Equipamento', backref='setor_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'filial_id': self.filial_id,
            'filial_tag': self.filial_ref.tag if self.filial_ref else None,
            'filial_descricao': self.filial_ref.descricao if self.filial_ref else None,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    foto = db.Column(db.String(255), nullable=True)  # Campo foto adicionado
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'descricao': self.descricao,
            'setor_id': self.setor_id,
            'setor_tag': self.setor_ref.tag if self.setor_ref else None,
            'setor_descricao': self.setor_ref.descricao if self.setor_ref else None,
            'filial_id': self.setor_ref.filial_id if self.setor_ref else None,
            'filial_tag': self.setor_ref.filial_ref.tag if self.setor_ref and self.setor_ref.filial_ref else None,
            'filial_descricao': self.setor_ref.filial_ref.descricao if self.setor_ref and self.setor_ref.filial_ref else None,
            'foto': self.foto,  # Campo foto incluído no retorno
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_criacao': self.usuario_criacao
        }


class Chamado(db.Model):
    __tablename__ = 'chamados'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)  # baixa, media, alta, seguranca
    status = db.Column(db.String(20), nullable=False, default='aberto')  # aberto, em_andamento, resolvido, fechado
    solicitante = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Relacionamentos
    filial_chamado = db.relationship('Filial', backref='chamados', lazy=True)
    setor_chamado = db.relationship('Setor', backref='chamados', lazy=True)
    equipamento_chamado = db.relationship('Equipamento', backref='chamados', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'filial_id': self.filial_id,
            'filial_tag': self.filial_chamado.tag if self.filial_chamado else None,
            'filial_descricao': self.filial_chamado.descricao if self.filial_chamado else None,
            'setor_id': self.setor_id,
            'setor_tag': self.setor_chamado.tag if self.setor_chamado else None,
            'setor_descricao': self.setor_chamado.descricao if self.setor_chamado else None,
            'equipamento_id': self.equipamento_id,
            'equipamento_tag': self.equipamento_chamado.tag if self.equipamento_chamado else None,
            'equipamento_descricao': self.equipamento_chamado.descricao if self.equipamento_chamado else None,
            'prioridade': self.prioridade,
            'status': self.status,
            'solicitante': self.solicitante,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'usuario_criacao': self.usuario_criacao
        }


class OrdemServico(db.Model):
    __tablename__ = 'ordens_servico'
    
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=True)  # Pode ser criada sem chamado
    descricao = db.Column(db.Text, nullable=False)
    tipo_manutencao = db.Column(db.String(50), nullable=False)  # corretiva, melhoria, setup, pmoc, inspecao, assistencia_tecnica
    oficina = db.Column(db.String(50), nullable=False)  # mecanica, eletrica, automacao, eletromecanico, operacional
    condicao_ativo = db.Column(db.String(20), nullable=False)  # parado, funcionando
    qtd_pessoas = db.Column(db.Integer, nullable=False, default=1)
    horas = db.Column(db.Float, nullable=False, default=1.0)
    hh = db.Column(db.Float, nullable=False)  # qtd_pessoas * horas (calculado automaticamente)
    prioridade = db.Column(db.String(20), nullable=False)  # baixa, media, alta, seguranca, preventiva
    status = db.Column(db.String(20), nullable=False, default='aberta')  # aberta, programada, em_andamento, concluida, cancelada
    
    # Dados do ativo (podem ser alterados)
    filial_id = db.Column(db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    
    # Dados da empresa e usuário
    empresa = db.Column(db.String(100), nullable=False)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    usuario_responsavel = db.Column(db.String(100), nullable=True)  # Usuário que executará a OS

    # Campos para integração com PMP
    pmp_id = db.Column(db.Integer, db.ForeignKey('pmps.id'), nullable=True)
    data_proxima_geracao = db.Column(db.Date, nullable=True)
    frequencia_origem = db.Column(db.String(20), nullable=True)
    numero_sequencia = db.Column(db.Integer, nullable=False, default=1)
    
    # Datas
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_programada = db.Column(db.Date, nullable=True)  # Data programada para execução
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    chamado_origem = db.relationship('Chamado', backref='ordem_servico', lazy=True)
    filial_os = db.relationship('Filial', backref='ordens_servico', lazy=True)
    setor_os = db.relationship('Setor', backref='ordens_servico', lazy=True)
    equipamento_os = db.relationship('Equipamento', backref='ordens_servico', lazy=True)
    
    def __init__(self, **kwargs):
        super(OrdemServico, self).__init__(**kwargs)
        # Calcular HH automaticamente
        if self.qtd_pessoas and self.horas:
            self.hh = self.qtd_pessoas * self.horas
    
    def calcular_hh(self):
        """Recalcula o HH baseado na quantidade de pessoas e horas"""
        self.hh = self.qtd_pessoas * self.horas
        return self.hh
    
    def to_dict(self):
        return {
            'id': self.id,
            'chamado_id': self.chamado_id,
            'descricao': self.descricao,
            'tipo_manutencao': self.tipo_manutencao,
            'oficina': self.oficina,
            'condicao_ativo': self.condicao_ativo,
            'qtd_pessoas': self.qtd_pessoas,
            'horas': self.horas,
            'hh': self.hh,
            'prioridade': self.prioridade,
            'status': self.status,
            'filial_id': self.filial_id,
            'filial_tag': self.filial_os.tag if self.filial_os else None,
            'filial_descricao': self.filial_os.descricao if self.filial_os else None,
            'setor_id': self.setor_id,
            'setor_tag': self.setor_os.tag if self.setor_os else None,
            'setor_descricao': self.setor_os.descricao if self.setor_os else None,
            'equipamento_id': self.equipamento_id,
            'equipamento_tag': self.equipamento_os.tag if self.equipamento_os else None,
            'equipamento_descricao': self.equipamento_os.descricao if self.equipamento_os else None,
            'empresa': self.empresa,
            'usuario_criacao': self.usuario_criacao,
            'usuario_responsavel': self.usuario_responsavel,
            'pmp_id': self.pmp_id,
            'data_proxima_geracao': self.data_proxima_geracao.isoformat() if self.data_proxima_geracao else None,
            'frequencia_origem': self.frequencia_origem,
            'numero_sequencia': self.numero_sequencia,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_programada': self.data_programada.isoformat() if self.data_programada else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class MaterialEstoque(db.Model):
    __tablename__ = 'materiais_estoque'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(50), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    unidade = db.Column(db.String(20), nullable=False, default='UN')  # UN, KG, L, M, etc.
    valor_unitario = db.Column(db.Float, nullable=False, default=0.0)
    quantidade_estoque = db.Column(db.Float, nullable=False, default=0.0)
    estoque_minimo = db.Column(db.Float, nullable=False, default=0.0)
    categoria = db.Column(db.String(100), nullable=True)
    fornecedor = db.Column(db.String(200), nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Dados da empresa
    empresa = db.Column(db.String(100), nullable=False)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    
    # Datas
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'unidade': self.unidade,
            'valor_unitario': self.valor_unitario,
            'quantidade_estoque': self.quantidade_estoque,
            'estoque_minimo': self.estoque_minimo,
            'categoria': self.categoria,
            'fornecedor': self.fornecedor,
            'ativo': self.ativo,
            'empresa': self.empresa,
            'usuario_criacao': self.usuario_criacao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class ExecucaoOS(db.Model):
    __tablename__ = 'execucoes_os'
    
    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'), nullable=False)
    
    # Dados de execução
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    lista_execucao_status = db.Column(db.String(2), nullable=False, default='C')  # C = Conforme, NC = Não Conforme
    observacoes = db.Column(db.Text, nullable=True)
    
    # Dados do executor
    executor = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    
    # Datas de controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    ordem_servico = db.relationship('OrdemServico', backref='execucoes', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'os_id': self.os_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'lista_execucao_status': self.lista_execucao_status,
            'observacoes': self.observacoes,
            'executor': self.executor,
            'empresa': self.empresa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class MaterialUtilizado(db.Model):
    __tablename__ = 'materiais_utilizados'
    
    id = db.Column(db.Integer, primary_key=True)
    execucao_id = db.Column(db.Integer, db.ForeignKey('execucoes_os.id'), nullable=False)
    
    # Tipo de material
    tipo_material = db.Column(db.String(20), nullable=False)  # 'estoque' ou 'avulso'
    
    # Para material de estoque
    material_estoque_id = db.Column(db.Integer, db.ForeignKey('materiais_estoque.id'), nullable=True)
    
    # Para material avulso
    nome_material = db.Column(db.String(200), nullable=True)
    valor_unitario = db.Column(db.Float, nullable=True)
    
    # Campos comuns
    quantidade = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)  # quantidade * valor_unitario
    
    # Dados de controle
    empresa = db.Column(db.String(100), nullable=False)
    usuario_criacao = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    execucao = db.relationship('ExecucaoOS', backref='materiais_utilizados', lazy=True)
    material_estoque = db.relationship('MaterialEstoque', backref='utilizacoes', lazy=True)
    
    def __init__(self, **kwargs):
        super(MaterialUtilizado, self).__init__(**kwargs)
        # Calcular valor total automaticamente
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
    
    def calcular_valor_total(self):
        """Recalcula o valor total baseado na quantidade e valor unitário"""
        if self.tipo_material == 'estoque' and self.material_estoque:
            self.valor_unitario = self.material_estoque.valor_unitario
        
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        return self.valor_total
    
    def to_dict(self):
        material_info = {}
        if self.tipo_material == 'estoque' and self.material_estoque:
            material_info = {
                'nome_material': self.material_estoque.nome,
                'codigo_material': self.material_estoque.codigo,
                'unidade': self.material_estoque.unidade
            }
        else:
            material_info = {
                'nome_material': self.nome_material,
                'codigo_material': None,
                'unidade': 'UN'
            }
        
        return {
            'id': self.id,
            'execucao_id': self.execucao_id,
            'tipo_material': self.tipo_material,
            'material_estoque_id': self.material_estoque_id,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.valor_total,
            'empresa': self.empresa,
            'usuario_criacao': self.usuario_criacao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            **material_info
        }

