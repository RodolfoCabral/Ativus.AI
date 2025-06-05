document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('login-form');
  const loginMessage = document.getElementById('login-message');
  
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      // Limpar mensagens anteriores
      loginMessage.textContent = '';
      loginMessage.className = 'message';
      loginMessage.style.display = 'none';
      
      // Enviar requisição para a API de login
      fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Login bem-sucedido
          loginMessage.textContent = 'Login realizado com sucesso! Redirecionando...';
          loginMessage.classList.add('success');
          loginMessage.style.display = 'block';
          
          // Redirecionar após um breve delay
          setTimeout(() => {
            window.location.href = '/dashboard';  // Redireciona para o dashboard
          }, 1500);
        } else {
          // Login falhou
          loginMessage.textContent = data.message || 'Erro ao fazer login. Verifique suas credenciais.';
          loginMessage.classList.add('error');
          loginMessage.style.display = 'block';
        }
      })
      .catch(error => {
        console.error('Erro:', error);
        loginMessage.textContent = 'Erro de conexão. Tente novamente mais tarde.';
        loginMessage.classList.add('error');
        loginMessage.style.display = 'block';
      });
    });
  }
  
  // Funcionalidade para o botão "Esqueci minha senha"
  const forgotPasswordBtn = document.getElementById('forgot-password');
  if (forgotPasswordBtn) {
    forgotPasswordBtn.addEventListener('click', function() {
      alert('Funcionalidade de recuperação de senha será implementada em breve.');
    });
  }
  
  // Funcionalidade para o botão "Assinar plano"
  // const signupBtn = document.getElementById('signup-btn');
  // if (signupBtn) {
  //   signupBtn.addEventListener('click', function() {
  //     alert('Funcionalidade de assinatura será implementada em breve.');
  //   });
  // }
});
