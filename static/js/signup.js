document.addEventListener('DOMContentLoaded', function() {
  const signupForm = document.getElementById('signup-form');
  const signupMessage = document.getElementById('signup-message');
  
  // Máscara para o campo de telefone
  const phoneInput = document.getElementById('phone');
  if (phoneInput) {
    phoneInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 0) {
        // Formata como (XX) XXXXX-XXXX
        if (value.length <= 2) {
          value = `(${value}`;
        } else if (value.length <= 7) {
          value = `(${value.substring(0, 2)}) ${value.substring(2)}`;
        } else if (value.length <= 11) {
          value = `(${value.substring(0, 2)}) ${value.substring(2, 7)}-${value.substring(7)}`;
        } else {
          value = `(${value.substring(0, 2)}) ${value.substring(2, 7)}-${value.substring(7, 11)}`;
        }
      }
      e.target.value = value;
    });
  }
  
  // Efeitos visuais para melhorar a experiência do usuário
  const formInputs = document.querySelectorAll('.form-control');
  formInputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
      if (!this.value) {
        this.parentElement.classList.remove('focused');
      }
    });
  });
  
  if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const source = document.getElementById('source').value;
      const fullname = document.getElementById('fullname').value;
      const company = document.getElementById('company').value;
      const phone = document.getElementById('phone').value;
      
      // Limpar mensagens anteriores
      signupMessage.textContent = '';
      signupMessage.className = 'message';
      signupMessage.style.display = 'none';
      
      // Validações básicas
      if (!source || !fullname || !company || !phone) {
        signupMessage.textContent = 'Por favor, preencha todos os campos.';
        signupMessage.classList.add('error');
        signupMessage.style.display = 'block';
        return;
      }
      
      // Enviar requisição para a API de cadastro
      fetch('/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          source, 
          fullname, 
          company, 
          phone 
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Cadastro bem-sucedido
          signupForm.innerHTML = `
            <div class="success-checkmark">
              <div class="check-icon">
                <span class="icon-line line-tip"></span>
                <span class="icon-line line-long"></span>
                <div class="icon-circle"></div>
                <div class="icon-fix"></div>
              </div>
            </div>
            <h2 style="color: #4CAF50; margin-bottom: 1.5rem;">Cadastro realizado com sucesso!</h2>
            <p>Obrigado pelo seu interesse. Nossa equipe entrará em contato em breve.</p>
            <div class="actions" style="margin-top: 2rem;">
              <a href="/" class="btn btn-primary">Voltar para login</a>
            </div>
          `;
        } else {
          // Cadastro falhou
          signupMessage.textContent = data.message || 'Erro ao realizar cadastro. Tente novamente mais tarde.';
          signupMessage.classList.add('error');
          signupMessage.style.display = 'block';
        }
      })
      .catch(error => {
        console.error('Erro:', error);
        signupMessage.textContent = 'Erro de conexão. Tente novamente mais tarde.';
        signupMessage.classList.add('error');
        signupMessage.style.display = 'block';
      });
    });
  }
});
