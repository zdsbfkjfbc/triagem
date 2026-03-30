import os
import time
import uuid

import pytest
import requests

BASE_URL = os.getenv("TRIAGE_BASE_URL", "http://localhost:8000")
TEST_USER = os.getenv("TRIAGE_TEST_USER", "admin")
TEST_PASSWORD = os.getenv("TRIAGE_TEST_PASSWORD", "admin123")


def _post(path: str, **kwargs) -> requests.Response:
    return requests.post(f"{BASE_URL}{path}", timeout=10, **kwargs)


def _is_backend_available() -> bool:
    try:
        res = requests.get(f"{BASE_URL}/jobs", timeout=3)
        return res.status_code in (200, 401, 403)
    except requests.RequestException:
        return False


def get_token() -> str:
    res = _post("/auth/login", data={"username": TEST_USER, "password": TEST_PASSWORD})
    if res.status_code != 200:
        pytest.skip(f"Não foi possível autenticar no backend local ({res.status_code}).")
    token = res.json().get("access_token")
    if not token:
        pytest.skip("Backend respondeu sem access_token.")
    return token


def create_job(headers: dict) -> int:
    unique_title = f"Perf Test Job {int(time.time())}"
    res = _post(
        "/jobs",
        data={"title": unique_title, "description": "Vaga para teste de performance"},
        headers=headers,
    )
    if res.status_code != 200:
        pytest.skip(f"Não foi possível criar job para o teste ({res.status_code}).")
    payload = res.json()
    return int(payload["id"])


def test_batch_performance():
    if not _is_backend_available():
        pytest.skip("Backend local não está disponível em http://localhost:8000.")

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    job_id = create_job(headers)

    files = []
    unique = uuid.uuid4().hex
    for i in range(5):
        file_name = f"test_resume_{unique}_{i}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f"Candidato Teste {i}\nExperiência em Python e Performance.\nEspecialista em multithreading.")
        files.append(("files", (file_name, open(file_name, "rb"), "text/plain")))

    data = {
        "api_key": "sk-or-v1-fake-key",
        "job_id": str(job_id),
        "model_id": "google/gemini-2.0-flash-lite-preview-02-05:free",
    }

    t_start = time.time()
    try:
        res = _post("/triage/batch", data=data, files=files, headers=headers)
        elapsed = time.time() - t_start
        assert res.status_code == 202, f"Resposta inesperada: {res.status_code} - {res.text}"
        assert elapsed < 10
    finally:
        for _, (file_name, fh, _) in files:
            fh.close()
            if os.path.exists(file_name):
                os.remove(file_name)
