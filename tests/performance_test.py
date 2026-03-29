import requests
import time
import os

BASE_URL = "http://localhost:8000"

def get_token():
    print("🔑 Obtendo token de acesso...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
    return res.json().get("access_token")

def test_batch_performance():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar arquivos temporários para teste
    print("📝 Criando 5 currículos fictícios para teste de estresse...")
    files = []
    for i in range(5):
        fname = f"test_resume_{i}.txt"
        with open(fname, "w") as f:
            f.write(f"Candidato Teste {i}\nExperiência em Python e Performance.\nEspecialista em multithreading.")
        files.append(("files", (fname, open(fname, "rb"), "text/plain")))

    data = {
        "api_key": "sk-or-v1-fake-key", # Dummy key para teste de fluxo
        "job_id": 2,
        "model_id": "google/gemini-2.0-flash-lite-preview-02-05:free"
    }

    print("🚀 Disparando Lote de 5 currículos (Processamento Paralelo)...")
    t_start = time.time()
    
    try:
        # Nota: O endpoint é asíncrono (202 Accepted)
        res = requests.post(f"{BASE_URL}/triage/batch", data=data, files=files, headers=headers)
        if res.status_code == 202:
            print(f"✅ Lote aceito em {round(time.time() - t_start, 2)}s.")
            print("⏳ Verificando console do Backend para barra de progresso...")
        else:
            print(f"❌ Erro ao disparar lote: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Falha de conexão: {e}")
    finally:
        # Cleanup
        for _, (fname, fobj, _) in files:
            fobj.close()
            if os.path.exists(fname):
                os.remove(fname)

if __name__ == "__main__":
    test_batch_performance()
