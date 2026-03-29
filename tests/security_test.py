import requests
import json

BASE_URL = "http://localhost:8000"

def test_unauthorized_access():
    print("\n🔍 Testando acesso NÃO AUTORIZADO ao Talent Pool...")
    try:
        response = requests.get(f"{BASE_URL}/talent-pool")
        if response.status_code == 401:
            print("✅ SUCESSO: Acesso negado como esperado (401 Unauthorized).")
        else:
            print(f"❌ FALHA: Endpoint exposto! Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na conexão: {e} (Verifique se o backend está rodando em {BASE_URL})")

def test_login_and_access():
    print("\n🔐 Testando LOGIN e acesso AUTORIZADO...")
    login_data = {"username": "admin", "password": "admin123"}
    try:
        # FastAPI OAuth2PasswordRequestForm usa form-data
        login_res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")
            print("✅ SUCESSO: Login realizado. Token obtido.")
            
            headers = {"Authorization": f"Bearer {token}"}
            pool_res = requests.get(f"{BASE_URL}/talent-pool", headers=headers)
            if pool_res.status_code == 200:
                print(f"✅ SUCESSO: Acesso ao Talent Pool liberado ({len(pool_res.json())} candidatos).")
            else:
                print(f"❌ FALHA: Token rejeitado! Status: {pool_res.status_code}")
        else:
            print(f"❌ FALHA: Login falhou! Status: {login_res.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando Simulação de Pentest (Ciclo 1: Segurança)...")
    test_unauthorized_access()
    test_login_and_access()
