import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, make_response, jsonify
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from functools import wraps
import io
import requests
import markdown
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_default')

@app.template_filter('markdown')
def render_markdown(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=['fenced_code', 'tables'])

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
        raise ValueError("Database URL not found")
    conn = psycopg2.connect(url)
    return conn

def fix_relative_images(markdown_text, user, repo, branch='main'):
    """
    Procura por imagens Markdown com caminhos relativos e converte para URLs absolutas do GitHub Raw.
    Ex: ![Alt](img/foto.png) -> ![Alt](https://raw.githubusercontent.com/User/Repo/main/img/foto.png)
    """
    base_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/"
    
    def replace_link(match):
        alt_text = match.group(1)
        link = match.group(2)
        
        # Se já for um link completo (http/https), não mexe
        if link.startswith('http://') or link.startswith('https://'):
            return match.group(0)
        
        # Se for relativo, adiciona a base do GitHub
        # Remove ./ do início se houver
        clean_link = link.lstrip('./')
        return f"![{alt_text}]({base_url}{clean_link})"

    # Regex para encontrar imagens Markdown: ![alt](link)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.sub(pattern, replace_link, markdown_text)

def get_github_readme(github_url):
    try:
        if not github_url or 'github.com' not in github_url:
            return None
        
        parts = github_url.rstrip('/').split('/')
        if len(parts) < 2:
            return None
            
        user = parts[-2]
        repo = parts[-1]
        
        # 1. Descobrir qual é a branch padrão (main ou master)
        repo_api_url = f"https://api.github.com/repos/{user}/{repo}"
        repo_data = requests.get(repo_api_url).json()
        default_branch = repo_data.get('default_branch', 'main')
        
        # 2. Pegar o conteúdo do README
        readme_api_url = f"https://api.github.com/repos/{user}/{repo}/readme"
        headers = {'Accept': 'application/vnd.github.v3.raw'}
        
        response = requests.get(readme_api_url, headers=headers)
        
        if response.status_code == 200:
            raw_text = response.text
            # 3. Corrigir links de imagens relativos
            fixed_text = fix_relative_images(raw_text, user, repo, default_branch)
            return fixed_text
            
        return None
    except Exception as e:
        print(f"Error fetching README: {e}")
        return None

@app.route('/profile_image')
def profile_image():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT avatar_data FROM portifolio_profile LIMIT 1")
        record = cur.fetchone()
        
        if record and record[0]:
            response = make_response(send_file(
                io.BytesIO(record[0]),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name='profile.jpg'
            ))
            response.headers['Cache-Control'] = 'public, max-age=86400'
            return response
            
    except Exception:
        pass
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('static', filename='yo.jpg'))

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT id, name, role, bio, avatar_url, github_link, linkedin_link, resume_link FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', profile=profile, projects=projects)

@app.route('/project/<int:id>')
def project_details(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM portifolio_projects WHERE id = %s', (id,))
    project = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not project:
        return redirect(url_for('index'))
        
    return render_template('project_details.html', project=project)

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

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT id, name, role, bio, avatar_url, github_link, linkedin_link, resume_link FROM portifolio_profile LIMIT 1')
    profile = cur.fetchone()
    
    cur.execute('SELECT * FROM portifolio_projects ORDER BY created_at DESC')
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin.html', profile=profile, projects=projects)

@app.route('/admin/fetch_readme', methods=['POST'])
@login_required
def fetch_readme():
    data = request.get_json()
    github_url = data.get('github_url')
    
    if not github_url:
        return jsonify({'error': 'URL do GitHub não fornecida'}), 400
        
    readme_content = get_github_readme(github_url)
    
    if readme_content:
        return jsonify({'content': readme_content})
    else:
        return jsonify({'error': 'Não foi possível encontrar o README. Verifique a URL e se o repositório é público.'}), 404

@app.route('/admin/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.form
    file = request.files.get('avatar_file')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM portifolio_profile LIMIT 1")
        exists = cur.fetchone()
        
        image_data = None
        if file and file.filename:
            image_data = file.read()

        if exists:
            query = """
                UPDATE portifolio_profile
                SET name=%s, role=%s, bio=%s, github_link=%s, linkedin_link=%s, resume_link=%s
            """
            params = [data['name'], data['role'], data['bio'], 
                      data['github_link'], data['linkedin_link'], data['resume_link']]
            
            if image_data:
                query += ", avatar_data=%s"
                params.append(image_data)
                
            query += " WHERE id=%s"
            params.append(exists[0])
            
            cur.execute(query, tuple(params))
        else:
            cur.execute("""
                INSERT INTO portifolio_profile (name, role, bio, avatar_data, github_link, linkedin_link, resume_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data['name'], data['role'], data['bio'], image_data, 
                  data['github_link'], data['linkedin_link'], data['resume_link']))
            
        conn.commit()
        flash('Perfil atualizado!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro: {str(e)}', 'error')
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
        flash(f'Erro: {str(e)}', 'error')
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
            flash(f'Erro: {str(e)}', 'error')
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
        flash(f'Erro: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
