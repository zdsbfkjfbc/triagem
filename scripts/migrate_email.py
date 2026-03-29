import sqlite3
import os

DB_PATH = "d:/Desenvolvimento/Triage/triage.db"

def migrate():
    print(f"🔄 Conectando ao banco de dados: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ Erro: Arquivo de banco de dados não encontrado.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica se o banco existe e tenta adicionar a coluna
        print("🛠️ Adicionando coluna 'email' à tabela 'candidates'...")
        cursor.execute("ALTER TABLE candidates ADD COLUMN email TEXT;")
        
        conn.commit()
        print("✅ Sucesso: Coluna 'email' adicionada com sucesso!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Info: A coluna 'email' já existe no banco de dados.")
        else:
            print(f"❌ Erro de Operação SQLite: {e}")
    except Exception as e:
        print(f"❌ Erro Inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()
