import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    url = os.environ.get('SUPABASE_URL') or os.environ.get('DATABASE_URL')
    
    if not url:
        print("Error: Database URL not found in .env")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()

        print("Setting up database tables...")

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
        
        try:
            cur.execute("ALTER TABLE portifolio_profile ADD COLUMN IF NOT EXISTS avatar_data BYTEA;")
            conn.commit()
        except Exception:
            conn.rollback()

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

        cur.execute("SELECT COUNT(*) FROM portifolio_profile")
        if cur.fetchone()[0] == 0:
            print("Inserting initial profile data...")
            cur.execute("""
                INSERT INTO portifolio_profile (name, role, bio, avatar_url, github_link, linkedin_link, resume_link)
                VALUES (
                    'Dev Name',
                    'Software Developer',
                    'Bio description here...',
                    'yo.jpg',
                    '#',
                    '#',
                    '#'
                )
            """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database setup completed successfully.")

    except Exception as e:
        print(f"Database setup failed: {e}")

if __name__ == "__main__":
    create_tables()
