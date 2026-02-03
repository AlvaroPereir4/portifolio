# Portfólio Profissional

Uma aplicação de portfólio dinâmica desenvolvida com Python (Flask) e PostgreSQL, apresentando um painel administrativo seguro e arquitetura frontend moderna.

## Stack Tecnológico

- **Backend**: Python, Flask, Psycopg2
- **Frontend**: HTML5, CSS3, JavaScript (Canvas API)
- **Banco de Dados**: PostgreSQL
- **Design**: Tema Escuro Personalizado, Layout de Grid Responsivo

## Funcionalidades

- **Painel Administrativo**: Área protegida para gerenciamento de conteúdo (perfil e projetos).
- **Processamento de Imagem**: Recorte no lado do cliente e armazenamento binário no banco de dados.
- **Persistência de Dados**: Gerenciamento centralizado de dados via PostgreSQL.
- **Performance**: Cache HTTP e carregamento otimizado de ativos.
- **Interface Interativa**: Animação de fundo (rede neural) e estados de carregamento (skeleton loading).

## Configuração Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuração de Ambiente**
   Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
   ```env
   DATABASE_URL=postgresql://usuario:senha@host:porta/nome_banco
   ADMIN_PASSWORD=sua_senha_segura
   SECRET_KEY=sua_chave_secreta_aleatoria
   ```

5. **Inicialização do Banco de Dados**
   ```bash
   python db_setup.py
   ```

6. **Executar a aplicação**
   ```bash
   python app.py
   ```
   Acesse: `http://127.0.0.1:5000`

## Nota de Segurança

Certifique-se de que o arquivo `.env` esteja incluído no seu `.gitignore` para evitar que credenciais sensíveis sejam enviadas para o controle de versão.

## Licença

Licença MIT
