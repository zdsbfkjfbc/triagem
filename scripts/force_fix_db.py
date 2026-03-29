import sqlite3
import os
import shutil

DB_PATH = "d:/Desenvolvimento/Triage/triage.db"

def force_cleanup_and_migrate():
    print("🧹 Iniciando Saneamento Total...")
    
    # 1. Limpeza de Cache Python
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))
    print("✅ Cache __pycache__ e .pyc removidos.")

    # 2. Migração Física
    if not os.path.exists(DB_PATH):
        print("ℹ️ Banco de dados não encontrado, será criado pelo SQLAlchemy.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica colunas existentes
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "email" not in columns:
            print("🛠️ Aplicando migração: Adicionando coluna 'email'...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN email TEXT;")
            conn.commit()
            print("✅ Coluna 'email' injetada com sucesso.")
        else:
            print("✅ Coluna 'email' já confirmada no banco de dados.")
            
        conn.close()
    except Exception as e:
        print(f"❌ Erro na migração física: {e}")

if __name__ == "__main__":
    force_cleanup_and_migrate()
