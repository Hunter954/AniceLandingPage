# Portal Anice — Flask + PostgreSQL

Projeto responsivo inspirado no layout enviado, com frontend completo e painel administrativo premium.

## Recursos
- Site institucional responsivo em Bootstrap 5 + Bootstrap Icons.
- Painel `/admin` com menus separados por seção.
- Gerenciamento de textos, cores, imagens, botões, links, agenda, projetos, notícias, galeria e depoimentos.
- PostgreSQL em produção e SQLite como fallback local.
- Uploads persistentes em volume do Railway.
- Seed automático com conteúdo placeholder.

## Rodar localmente
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```
Acesse `http://localhost:5000` e `http://localhost:5000/admin`.

Credenciais iniciais locais:
- E-mail: `admin@site.com`
- Senha: `TroqueAgora123!`

Troque a senha no painel imediatamente.

## Deploy no Railway
1. Envie o projeto ao GitHub.
2. Crie um projeto no Railway a partir do repositório.
3. Adicione um serviço PostgreSQL.
4. Defina as variáveis `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `UPLOAD_FOLDER=/app/uploads`.
5. Crie um Volume e monte em `/app/uploads`.
6. O Railway detectará o `Procfile`/`railway.json` e iniciará o Gunicorn.

## Observação visual
As imagens reais da campanha não foram incorporadas. Faça o upload pelo painel em Identidade, Hero, Sobre, CTA, Projetos, Notícias e Galeria.
