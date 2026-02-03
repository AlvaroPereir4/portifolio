import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    url = os.environ.get('SUPABASE_URL') or os.environ.get('DATABASE_URL')
    
    if not url:
        print("Erro: Variável de conexão (SUPABASE_URL ou DATABASE_URL) não encontrada no arquivo .env")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()

        print("Criando/Atualizando tabelas com prefixo 'portifolio_'...")

        # 1. Tabela de Perfil (portifolio_profile)
        # Adicionando coluna avatar_data (BYTEA) para salvar a imagem binária
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portifolio_profile (
                id SERIAL PRIMARY KEY,
                name TEXT,
                role TEXT,
                bio TEXT,
                avatar_url TEXT,
                avatar_data BYTEA, 
                github_link TEXT,
                linkedin_link TEXT,
                resume_link TEXT
            );
        """)
        
        # Tenta adicionar a coluna avatar_data caso a tabela já exista sem ela
        try:
            cur.execute("ALTER TABLE portifolio_profile ADD COLUMN IF NOT EXISTS avatar_data BYTEA;")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Nota: {e}")

        # 2. Tabela de Projetos (portifolio_projects)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portifolio_projects (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                github_link TEXT,
                project_link TEXT,
                doc_link TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Inserir dados iniciais se a tabela de perfil estiver vazia
        cur.execute("SELECT COUNT(*) FROM portifolio_profile")
        if cur.fetchone()[0] == 0:
            print("Inserindo dados iniciais de perfil...")
            cur.execute("""
                INSERT INTO portifolio_profile (name, role, bio, avatar_url, github_link, linkedin_link, resume_link)
                VALUES (
                    'Alvaro Pereira',
                    'Desenvolvedor de Softwares',
                    'Desenvolvedor Python especializado em automação e integração de sistemas...',
                    'yo.jpg',
                    'https://github.com/AlvaroPereir4',
                    'https://www.linkedin.com/in/alvaro-pereira-b5b2a8227/',
                    '#'
                )
            """)

        conn.commit()
        cur.close()
        conn.close()
        print("Sucesso! Tabelas atualizadas.")

    except Exception as e:
        print(f"Erro ao conectar ou criar tabelas: {e}")

if __name__ == "__main__":
    create_tables()
