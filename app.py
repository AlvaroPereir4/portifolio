import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura' 

# --- Decorator para proteger rotas ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    url = os.environ.get('SUPABASE_URL') or os.environ.get('DATABASE_URL')
    if not url:
        raise ValueError("Nenhuma URL de banco de dados encontrada no .env")
    conn = psycopg2.connect(url)
    return conn

# --- Rota Pública ---
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', profile=profile, projects=projects)

# --- Autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        
        if password == admin_pass:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Senha incorreta.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- Rotas de Admin (Protegidas) ---

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin.html', profile=profile, projects=projects)

@app.route('/admin/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
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
@login_required
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
@login_required
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
    
    cur.execute("SELECT * FROM portifolio_projects WHERE id = %s", (id,))
    project = cur.fetchone()
    conn.close()
    
    if not project:
        flash('Projeto não encontrado.', 'error')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_project.html', project=project)

@app.route('/admin/project/delete/<int:id>', methods=['POST'])
@login_required
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
