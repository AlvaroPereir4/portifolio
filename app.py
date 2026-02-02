import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura' 

def get_db_connection():
    # Tenta pegar SUPABASE_URL ou DATABASE_URL
    url = os.environ.get('SUPABASE_URL') or os.environ.get('DATABASE_URL')
    if not url:
        raise ValueError("Nenhuma URL de banco de dados encontrada no .env")
    conn = psycopg2.connect(url)
    return conn

# --- Rota Pública (Visualização) ---
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Busca perfil
    cur.execute('SELECT * FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    # Busca projetos
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', profile=profile, projects=projects)

# --- Rotas de Admin ---

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Dados para edição
    cur.execute('SELECT * FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin.html', profile=profile, projects=projects)

@app.route('/admin/profile/update', methods=['POST'])
def update_profile():
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verifica se já existe perfil
        cur.execute("SELECT id FROM portifolio_profile LIMIT 1")
        exists = cur.fetchone()
        
        if exists:
            cur.execute("""
                UPDATE portifolio_profile
                SET name=%s, role=%s, bio=%s, avatar_url=%s, github_link=%s, linkedin_link=%s, resume_link=%s
                WHERE id=%s
            """, (data['name'], data['role'], data['bio'], data['avatar_url'], 
                  data['github_link'], data['linkedin_link'], data['resume_link'], exists[0]))
        else:
            cur.execute("""
                INSERT INTO portifolio_profile (name, role, bio, avatar_url, github_link, linkedin_link, resume_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data['name'], data['role'], data['bio'], data['avatar_url'], 
                  data['github_link'], data['linkedin_link'], data['resume_link']))
            
        conn.commit()
        flash('Perfil atualizado!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/project/add', methods=['POST'])
def add_project():
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO portifolio_projects (title, description, github_link, project_link, doc_link)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['title'], data['description'], data['github_link'] or None, 
              data['project_link'] or None, data['doc_link'] or None))
        conn.commit()
        flash('Projeto adicionado!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/project/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        data = request.form
        try:
            cur.execute("""
                UPDATE portifolio_projects
                SET title=%s, description=%s, github_link=%s, project_link=%s, doc_link=%s
                WHERE id=%s
            """, (data['title'], data['description'], data['github_link'] or None, 
                  data['project_link'] or None, data['doc_link'] or None, id))
            conn.commit()
            flash('Projeto atualizado!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f'Erro: {e}', 'error')
        finally:
            conn.close()
    
    # GET: Mostrar formulário de edição
    cur.execute("SELECT * FROM portifolio_projects WHERE id = %s", (id,))
    project = cur.fetchone()
    conn.close()
    
    if not project:
        flash('Projeto não encontrado.', 'error')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_project.html', project=project)

@app.route('/admin/project/delete/<int:id>', methods=['POST'])
def delete_project(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM portifolio_projects WHERE id = %s", (id,))
        conn.commit()
        flash('Projeto excluído.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro: {e}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
