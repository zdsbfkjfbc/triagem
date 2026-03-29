import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database.repository import TriageRepository
from src.infrastructure.security.auth import AuthManager

def seed():
    repo = TriageRepository()
    auth = AuthManager()
    
    with repo.get_session() as session:
        # Verifica se já existem usuários
        from src.infrastructure.database.models import User
        users = session.query(User).all()
        
        if not users:
            print("🌱 Semeando usuário administrativo inicial...")
            auth.create_user(session, "admin", "admin123", role="admin")
            print("✅ Usuário 'admin' criado com sucesso! (Senha: admin123)")
        else:
            print(f"ℹ️ {len(users)} usuários encontrados:")
            for u in users:
                print(f" - ID: {u.id} | Username: {u.username} | Role: {u.role}")
            
            if not any(u.username == "admin" for u in users):
                print("⚠️ Usuário 'admin' não encontrado. Criando...")
                auth.create_user(session, "admin", "admin123", role="admin")
                print("✅ Usuário 'admin' criado com sucesso!")

if __name__ == "__main__":
    seed()
