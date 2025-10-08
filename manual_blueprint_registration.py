
# Adicionar no app.py após outras blueprints
print("🔧 Forçando registro manual das blueprints PMP...")

# Registro forçado da blueprint pmp_os_api
try:
    from routes.pmp_os_api import pmp_os_api_bp
    if 'pmp_os_api' not in app.blueprints:
        app.register_blueprint(pmp_os_api_bp)
        print("✅ pmp_os_api_bp registrada manualmente")
    else:
        print("⚠️ pmp_os_api_bp já estava registrada")
except Exception as e:
    print(f"❌ Erro ao registrar pmp_os_api_bp: {e}")

# Registro forçado da blueprint pmp_auto_status
try:
    from routes.pmp_auto_status import pmp_auto_status_bp
    if 'pmp_auto_status' not in app.blueprints:
        app.register_blueprint(pmp_auto_status_bp)
        print("✅ pmp_auto_status_bp registrada manualmente")
    else:
        print("⚠️ pmp_auto_status_bp já estava registrada")
except Exception as e:
    print(f"❌ Erro ao registrar pmp_auto_status_bp: {e}")

# Verificar rotas após registro manual
pmp_routes = [r.rule for r in app.url_map.iter_rules() if '/api/pmp/' in r.rule]
print(f"📊 Total de rotas PMP registradas: {len(pmp_routes)}")
