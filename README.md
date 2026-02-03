# Portfólio

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=F7DF1E)

## Visão Geral do Projeto

Este projeto representa a transição de um desenvolvimento web estático para uma arquitetura de aplicação dinâmica e orientada a dados. Ele serve como um portfólio pessoal gerenciado inteiramente através de um painel administrativo seguro, eliminando a necessidade de alterações no código para atualizar o conteúdo.

A filosofia central por trás deste desenvolvimento foi construir um sistema robusto e autossuficiente que aproveita capacidades modernas de banco de dados e tecnologias de frontend interativas, sem depender de frameworks externos pesados.

## Destaques da Arquitetura

### Integração com Banco de Dados (Supabase)
Diferente de portfólios estáticos tradicionais, esta aplicação persiste todos os dados — incluindo informações de perfil, detalhes de projetos e ativos de mídia — em um banco de dados PostgreSQL gerenciado pelo Supabase. Isso garante a integridade dos dados e permite atualizações em tempo real.

### Armazenamento Binário de Imagens
Uma inovação técnica chave neste projeto é o tratamento de ativos de mídia. Em vez de depender de serviços externos de armazenamento de objetos (como AWS S3) ou sistemas de arquivos locais, as imagens de perfil são processadas e armazenadas diretamente no banco de dados PostgreSQL usando colunas do tipo `BYTEA` (dados binários). Essa abordagem centraliza a estratégia de backup e simplifica a arquitetura de implantação.

### Rede Neural Interativa
O frontend apresenta uma animação de fundo "Rede Neural" personalizada. Ela foi desenvolvida usando a API nativa do HTML5 Canvas e JavaScript puro, evitando bibliotecas gráficas pesadas. O sistema gera partículas que interagem com o movimento do mouse do usuário, criando uma experiência visual performática e envolvente que reflete o tema de conectividade e automação.

### Administração Segura
A aplicação inclui uma estrutura de rotas protegidas para o gerenciamento de conteúdo. Ela apresenta:
- Autenticação baseada em sessão.
- Configuração de credenciais sensíveis via variáveis de ambiente.
- Capacidades CRUD (Criar, Ler, Atualizar, Deletar) completas para projetos.
- Processamento de imagem no lado do cliente (recorte e redimensionamento) antes do envio ao servidor.

## Stack Tecnológico

- **Backend**: Python (Flask) atuando como API RESTful e renderizador de templates.
- **Banco de Dados**: PostgreSQL (via Supabase) para dados relacionais e armazenamento binário.
- **Frontend**: Templates com Jinja2, Variáveis CSS3 para temas e JavaScript.
- **Processamento de Imagem**: Cropper.js para manipulação no frontend e Python para tratamento binário no backend.

---

### Implantação

A aplicação está atualmente implantada e acessível via Vercel.

[**-> Portifólio Online**](https://alvaro-portifolio-three.vercel.app/)
