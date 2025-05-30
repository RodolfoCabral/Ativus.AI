from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.urls import url_parse
from src import db, mail
from src.models.user import User, AccessRequest
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

auth_bp = Blueprint('auth', __name__)

# Formulários
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Redefinição de Senha')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    password2 = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Redefinir Senha')

class AccessRequestForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefone', validators=[DataRequired()])
    current_management = TextAreaField('Como é a realidade da sua manutenção hoje?', validators=[DataRequired()])
    submit = SubmitField('Solicitar Acesso')

# Rotas
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None:
            flash('Usuário não cadastrado.', 'error')
            return render_template('auth/login.html', form=form, request_access=True)
        
        if not user.check_password(form.password.data):
            flash('Senha incorreta.', 'error')
            return render_template('auth/login.html', form=form)
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Aqui enviaria o email com o link para redefinição de senha
            # Por enquanto, apenas simulamos o processo
            flash('Verifique seu email para instruções de redefinição de senha.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Usuário não cadastrado.', 'error')
            return render_template('auth/reset_password_request.html', form=form, request_access=True)
    
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Aqui verificaria o token e identificaria o usuário
    # Por enquanto, apenas simulamos o processo
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Aqui atualizaria a senha do usuário
        flash('Sua senha foi redefinida com sucesso.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = AccessRequestForm()
    if form.validate_on_submit():
        # Verificar se o email já está cadastrado como usuário
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este email já está cadastrado. Por favor, tente fazer login ou recuperar sua senha.', 'error')
            return redirect(url_for('auth.login'))
        
        # Verificar se já existe uma solicitação pendente para este email
        existing_request = AccessRequest.query.filter_by(email=form.email.data, status='pending').first()
        if existing_request:
            flash('Já existe uma solicitação de acesso pendente para este email.', 'info')
            return redirect(url_for('auth.login'))
        
        # Criar nova solicitação de acesso
        access_request = AccessRequest(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            current_management=form.current_management.data
        )
        db.session.add(access_request)
        db.session.commit()
        
        # Enviar email para o administrador
        try:
            msg = Message(
                'Nova Solicitação de Acesso - OS Management',
                recipients=['rodolfocabral@outlook.com.br']
            )
            msg.body = f'''
            Nova solicitação de acesso recebida:
            
            Nome: {form.name.data}
            Email: {form.email.data}
            Telefone: {form.phone.data}
            Realidade atual de manutenção: {form.current_management.data}
            
            Para aprovar esta solicitação, acesse o painel administrativo.
            '''
            mail.send(msg)
            flash('Sua solicitação de acesso foi enviada com sucesso! Entraremos em contato em breve.', 'success')
        except Exception as e:
            flash('Sua solicitação foi registrada, mas houve um problema ao enviar o email de notificação.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/request_access.html', form=form)
