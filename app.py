from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from urllib.parse import urlencode
from dateutil.parser import parse

import time
from datetime import datetime, timedelta, date

#===================================================================================================================================================================

# Configuração da aplicação Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configuração do banco de dados MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Dsbrol48@localhost/stellaengzoho'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#===================================================================================================================================================================


#===================================================================================================================================================================
class Projetos(db.Model):
    __tablename__ = 'projetos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_zoho = db.Column(db.String(100), nullable=True, default='')
    projeto_id = db.Column(db.String(50), nullable=True, unique=True)
    nome_projeto = db.Column(db.String(500))
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    
    # Relacionamento corrigido
    atividades = db.relationship(
        'Atividades', 
        back_populates='projeto', 
        foreign_keys='[Atividades.projeto_id]',
        primaryjoin='Projetos.projeto_id == Atividades.projeto_id'
    )


class Atividades(db.Model):
    __tablename__ = 'atividades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    atividade_id = db.Column(db.String(50), nullable=True)
    projeto_id = db.Column(db.String(50), db.ForeignKey('projetos.projeto_id'), nullable=True)
    codigo_inicio = db.Column(db.String(50), nullable=True)
    codigo_fim = db.Column(db.String(50), nullable=True)
    nome_atividade = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Planejado')
    key_zoho = db.Column(db.String(100), nullable=True, default='')
    
    # Relacionamento corrigido
    projeto = db.relationship(
        'Projetos',
        back_populates='atividades',
        foreign_keys=[projeto_id]
    )
#===================================================================================================================================================================
'''
class Projetos_Stella(db.Model):
    __tablename__ = 'projetos_stella'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_zoho = db.Column(db.String(100), nullable=True, default='')
    projeto_id = db.Column(db.String(50), nullable=True, unique=True)
    nome_projeto = db.Column(db.String(500))
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    
    # Relacionamento corrigido
    atividades = db.relationship(
        'Atividades', 
        back_populates='projeto_stella', 
        foreign_keys='[Atividades.projeto_id]',
        primaryjoin='Projetos.projeto_id == Atividades.projeto_id'
    )


class Atividades_Stella(db.Model):
    __tablename__ = 'atividades_stella'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    atividade_id = db.Column(db.String(50), nullable=True)
    projeto_id = db.Column(db.String(50), db.ForeignKey('projetos.projeto_id'), nullable=True)
    codigo_inicio = db.Column(db.String(50), nullable=True)
    codigo_fim = db.Column(db.String(50), nullable=True)
    nome_atividade = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Planejado')
    key_zoho = db.Column(db.String(100), nullable=True, default='')
    
    # Relacionamento corrigido
    projeto = db.relationship(
        'Projetos',
        back_populates='atividades_stella',
        foreign_keys=[projeto_id]
    )
'''
#===================================================================================================================================================================
class Projetos_Stella(db.Model):
    __tablename__ = 'projetos_stella'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_zoho = db.Column(db.String(100), nullable=True, default='')
    projeto_id = db.Column(db.String(50), nullable=True, unique=True)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    nome_projeto = db.Column(db.String(100), nullable=False, unique=True)


class Atividades_Stella(db.Model):
    __tablename__ = 'atividades_stella'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    atividade_id = db.Column(db.String(50), nullable=True)
    projeto_id = db.Column(db.String(50), nullable=True)
    codigo_inicio = db.Column(db.String(50), nullable=True)
    codigo_fim = db.Column(db.String(50), nullable=True)
    nome_atividade = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Planejado')
    key_zoho = db.Column(db.String(100), nullable=True, default='')


# Configurações do Zoho
class Config:
    ZOHO_ORG_ID = 'stella'
    CLIENT_ID = '1000.QSZ9W677KG8Q5HWZYXMTUF1Z1BMAOX'
    CLIENT_SECRET = 'acba342bc272601b06a469bb1c800107595f965781'
    REDIRECT_URI = 'http://localhost:5000/callback'
    API_BASE_URL = 'https://projectsapi.zoho.com/restapi'
    TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token'
    AUTH_URL = 'https://accounts.zoho.com/oauth/v2/auth'

# Funções auxiliares

LAST_API_CALL = None
REQUEST_DELAY = 1.2  # 1.2 segundos entre chamadas (50 reqs/min)

def corrigir_datas_nulas(projetos):
    from datetime import date, timedelta

    data_padrao_inicio = date(2000, 1, 1)
    data_padrao_fim = date(2000, 1, 2)

    for projeto in projetos:
        if not projeto.data_inicio:
            projeto.data_inicio = data_padrao_inicio
        if not projeto.data_fim:
            projeto.data_fim = data_padrao_fim
        for atividade in projeto.atividades:
            if not atividade.data_inicio:
                atividade.data_inicio = data_padrao_inicio
            if not atividade.data_fim:
                atividade.data_fim = data_padrao_fim

def make_zoho_request(url, headers, params=None):
    global LAST_API_CALL
    
    # Controla o rate limiting
    if LAST_API_CALL is not None:
        elapsed = (datetime.now() - LAST_API_CALL).total_seconds()
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
    
    response = requests.get(url, headers=headers, params=params)
    LAST_API_CALL = datetime.now()
    
    if response.status_code == 400 and "THROTTLES_LIMIT_EXCEEDED" in response.text:
        wait_time = 120  # 2 minutos (padrão Zoho)
        print(f"Limite excedido. Esperando {wait_time/60} minutos...")
        time.sleep(wait_time)
        return make_zoho_request(url, headers, params)  # Retry
    
    return response


def calcular_progresso(projeto_id):
    tarefas = Atividades.query.filter_by(projeto_id=projeto_id).all()
    if not tarefas:
        return 0
    
    concluidas = sum(1 for t in tarefas if t.status == 'Concluído')
    return int((concluidas / len(tarefas)) * 100)

def parse_zoho_date(date_str):
    """Converte a data da API Zoho para objeto datetime.date."""
    if not date_str or not isinstance(date_str, str) or date_str.strip() == '':
        return datetime.today().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return parse(date_str).date()
        except Exception as e:
            app.logger.warning(f"Erro ao converter data: {date_str} - {str(e)}")
            return datetime.today().date()


def corrigir_relacionamentos():
    with app.app_context():
        # 1. Verificar atividades com problemas
        atividades_problema = db.session.execute("""
            SELECT a.id, a.projeto_id 
            FROM atividades a 
            LEFT JOIN projetos p ON a.projeto_id = p.id 
            WHERE p.id IS NULL
        """).fetchall()
        
        # 2. Para cada atividade problemática
        for ap in atividades_problema:
            atividade_id, projeto_id = ap
            
            # Tentar encontrar o projeto correto
            projeto = Projetos.query.filter_by(projeto_id=projeto_id).first()
            
            if projeto:
                # Atualizar com o ID interno correto
                db.session.execute(
                    "UPDATE atividades SET projeto_id = :projeto_correto WHERE id = :atividade_id",
                    {'projeto_correto': projeto.id, 'atividade_id': atividade_id}
                )
            else:
                # Se não encontrar o projeto, remover a atividade
                db.session.execute(
                    "DELETE FROM atividades WHERE id = :atividade_id",
                    {'atividade_id': atividade_id}
                )
        
        db.session.commit()



def verificar_consistencia_projetos(projects):
    problemas = []
    for project in projects:
        projeto_zoho_id = str(project.get('id'))
        if not Projetos.query.filter_by(projeto_id=projeto_zoho_id).first():
            problemas.append(f"Projeto Zoho ID {projeto_zoho_id} não encontrado no banco")
    return problemas


def sanitize_data(data, field_limits):
    """
    Sanitiza os dados para garantir que estejam dentro dos limites do banco de dados
    field_limits = {'nome_do_campo': (tamanho_maximo, valor_padrao)}
    """
    sanitized = {}
    for field, value in data.items():
        if field in field_limits:
            max_len, default = field_limits[field]
            if value is None:
                sanitized[field] = default
            elif isinstance(value, str) and len(value) > max_len:
                sanitized[field] = value[:max_len-3] + '...'
            else:
                sanitized[field] = value
        else:
            sanitized[field] = value
    return sanitized


def build_headers():
    if 'access_token' not in session:
        raise ValueError("Token de acesso não encontrado na sessão. Faça login novamente.")
    return {
        'Authorization': f'Zoho-oauthtoken {session["access_token"]}',
        'Content-Type': 'application/json'
    }

def get_portal_id(headers):
    response = requests.get(f'{Config.API_BASE_URL}/portals/', headers=headers)
    if response.status_code != 200:
        raise Exception(f"Erro ao obter portal ID: {response.status_code} - {response.text}")
    
    data = response.json()
    if not data.get('portals'):
        raise Exception("Nenhum portal encontrado na resposta.")
    
    return data['portals'][0]['id']

def get_engineering_projects(portal_id, headers):
    response = requests.get(
        f'{Config.API_BASE_URL}/portal/{portal_id}/projects/',
        headers=headers,
        params={'status': 'active'}
    )
    if response.status_code != 200:
        raise Exception(f"Erro ao obter projetos: {response.status_code} - {response.text}")
    
    return response.json().get('projects', [])

def get_project_tasks(portal_id, project_id, headers):
    url = f"{Config.API_BASE_URL}/portal/{portal_id}/projects/{project_id}/tasks/"
    
    try:
        response = make_zoho_request(url, headers, params={"range": "1000"})
        
        if response.status_code == 204:
            return []
            
        if response.status_code != 200:
            raise Exception(f"Erro ao obter tarefas: {response.status_code} - {response.text}")
            
        return response.json().get("tasks", [])
        
    except Exception as e:
        app.logger.error(f"Falha ao buscar tarefas: {str(e)}")
        return []

'''
def parse_zoho_date(date_str):
    if not date_str:
        return None
    try:
        return parse(date_str).date()
    except Exception as e:
        print(f"Erro ao converter data: {date_str} -> {e}")
        return None
'''


@app.route('/get_atividades/<projeto_id>')
def get_atividades_por_projeto(projeto_id):
    atividades = Atividades.query.filter_by(projeto_id=projeto_id).all()
    atividades_data = [{'id': a.atividade_id, 'nome': a.nome_atividade, 'key_zoho':a.key_zoho} for a in atividades]
    return jsonify(atividades_data)
       

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    params = {
        'client_id': Config.CLIENT_ID,
        'redirect_uri': Config.REDIRECT_URI,
        'response_type': 'code',
        'scope': 'ZohoProjects.projects.READ ZohoProjects.tasks.READ ZohoProjects.portals.READ',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    auth_url = f'{Config.AUTH_URL}?{urlencode(params)}'
    return redirect(auth_url)


def atualizar_projetos(portal_id, headers):
    projects = get_engineering_projects(portal_id, headers)
    
    for project in projects:
        projeto_zoho_id = str(project.get('id'))
        projeto = Projetos.query.filter_by(projeto_id=projeto_zoho_id).first()
        
        dados_projeto = {
            'key_zoho': project.get('key', ''),
            'projeto_id': projeto_zoho_id,
            'nome_projeto': project.get('name', 'Projeto sem nome'),
            #'data_inicio': parse_zoho_date(project.get('start_date')),
            #'data_fim': parse_zoho_date(project.get('end_date')) or datetime.today().date()
            'data_inicio': parse_zoho_date(project.get('start_date')) or date(2000, 1, 1),
            'data_fim': parse_zoho_date(project.get('end_date')) or date(2000, 1, 2)
        }
        
        if not projeto:
            projeto = Projetos(**dados_projeto)
            db.session.add(projeto)
        else:
            for key, value in dados_projeto.items():
                setattr(projeto, key, value)
    
    db.session.commit()
    return projects

def atualizar_atividades(portal_id, headers, projects):
    try:
        with db.session.no_autoflush:
            for project in projects:
                projeto_zoho_id = str(project.get('id'))
                projeto_db = Projetos.query.filter_by(projeto_id=projeto_zoho_id).first()
                
                if not projeto_db:
                    app.logger.warning(f"Projeto {projeto_zoho_id} não encontrado")
                    continue
                
                tarefas = get_project_tasks(portal_id, projeto_zoho_id, headers)
                for tarefa in tarefas:
                    atividade_id = str(tarefa.get('id'))
                    key_zoho = str(tarefa.get('key'))

                    if not atividade_id:
                        continue
                    
                    # Garantir datas válidas
                    data_inicio = parse_zoho_date(tarefa.get('start_date')) or datetime.today().date()
                    data_fim = parse_zoho_date(tarefa.get('end_date')) or datetime.today().date()
                   
                    # Garantir data_fim não é anterior a data_inicio
                    #if data_fim < data_inicio:
                    #    data_fim = data_inicio
                    
                    dados = {
                        'atividade_id': atividade_id,
                        'projeto_id': projeto_db.projeto_id,
                        'codigo_inicio': atividade_id,
                        'codigo_fim': atividade_id,
                        'nome_atividade': tarefa.get('name', 'Atividade sem nome')[:500],
                        'descricao': tarefa.get('description', ''),
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'status': (tarefa.get('status', {}).get('name', 'Planejado'))[:100],
                        'key_zoho': key_zoho                      
                    }
                    
                    atividade = Atividades.query.filter_by(atividade_id=atividade_id).first()
                    if atividade:
                        for key, value in dados.items():
                            setattr(atividade, key, value)
                    else:
                        nova_atividade = Atividades(**dados)
                        db.session.add(nova_atividade)
                    
            db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao sincronizar atividades: {str(e)}")
        raise

@app.route('/atualizar_dados_zoho')
def atualizar_dados_zoho():
    try:
        headers = build_headers()
        portal_id = get_portal_id(headers)
        
        # Sincronizar projetos primeiro
        projects = atualizar_projetos(portal_id, headers)
        if not projects:
            return "Nenhum projeto encontrado", 404
        
        # Sincronizar atividades
        if atualizar_atividades(portal_id, headers, projects):
            return redirect(url_for('gantt'))
        else:
            return "Erro ao sincronizar atividades", 500
            
    except Exception as e:
        return f"Erro ao sincronizar dados: {str(e)}", 500



@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Erro: código de autorização não fornecido", 400

    try:
        data = {
            'grant_type': 'authorization_code',
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'redirect_uri': Config.REDIRECT_URI,
            'code': code
        }
        response = requests.post(Config.TOKEN_URL, data=data)
        
        if response.status_code != 200:
            return f"Erro ao obter token: {response.status_code} - {response.text}", 400
            
        tokens = response.json()
        if 'access_token' not in tokens:
            return "Token de acesso não encontrado na resposta", 400

        session['access_token'] = tokens['access_token']
        session['refresh_token'] = tokens.get('refresh_token')

        return atualizar_dados_zoho()
        
    except Exception as e:
        return f"Erro no processo de callback: {str(e)}", 500


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nova_atividade = Atividades(
            projeto_id=request.form['projeto_id'],
            codigo_inicio=request.form['codigo_inicio'],
            codigo_fim=request.form['codigo_fim'],
            nome_atividade=request.form['nome_atividade'],
            descricao=request.form['descricao'],
            data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d'),
            data_fim=datetime.strptime(request.form['data_fim'], '%Y-%m-%d'),
            status=request.form.get('status', 'Planejado')
        )
        db.session.add(nova_atividade)
        db.session.commit()
        return redirect(url_for('gantt'))

    # Carrega todos os projetos com suas atividades
    projetos = Projetos.query.options(db.joinedload(Projetos.atividades)).all()
    
    # Prepara os dados para o template
    projetos_data = []
    for projeto in projetos:
        projeto_dict = {
            'projeto_id': projeto.projeto_id,
            'nome_projeto': projeto.nome_projeto,
            'key_zoho': projeto.key_zoho,
            'atividades': []
        }
        
        for atividade in projeto.atividades:
            atividade_dict = {
                'codigo_inicio': atividade.codigo_inicio,
                'codigo_fim': atividade.codigo_fim,
                'nome_atividade': atividade.nome_atividade,
                'descricao': atividade.descricao or '',
                'data_inicio': atividade.data_inicio.strftime('%Y-%m-%d') if atividade.data_inicio else '',
                'data_fim': atividade.data_fim.strftime('%Y-%m-%d') if atividade.data_fim else '',
                'status': atividade.status,
                'key_zoho': atividade.key_zoho or ''
            }
            projeto_dict['atividades'].append(atividade_dict)
        
        projetos_data.append(projeto_dict)
    
    return render_template('cadastrar.html', projetos=projetos_data)

#=====================================================================================================================================================================================
@app.route('/salvar_atividade', methods=['POST'])
def salvar_atividade():
    try:
        # Obter dados do formulário
        projeto_id = request.form.get('projeto_id')
        atividade_id_inicio = request.form.get('atividade_id_inicio')
        atividade_id_fim = request.form.get('atividade_id_fim')
        
        # Buscar projeto original
        projeto = Projetos.query.filter_by(projeto_id=projeto_id).first()
        if not projeto:
            return jsonify({"status": "error", "message": "Projeto não encontrado"}), 404
        
        # Buscar atividades originais
        atividade_inicio = Atividades.query.filter_by(atividade_id=atividade_id_inicio).first() if atividade_id_inicio else None
        atividade_fim = Atividades.query.filter_by(atividade_id=atividade_id_fim).first() if atividade_id_fim else None
        
        # Verificar se projeto já existe na tabela stella e fazer UPDATE ou INSERT
        projeto_stella = Projetos_Stella.query.filter_by(projeto_id=projeto.projeto_id).first()
        
        if projeto_stella:
            # UPDATE se já existir
            projeto_stella.key_zoho = projeto.key_zoho
            projeto_stella.data_inicio = projeto.data_inicio
            projeto_stella.data_fim = projeto.data_fim
        else:
            # INSERT se não existir
            projeto_stella = Projetos_Stella(
                projeto_id=projeto.projeto_id,
                key_zoho=projeto.key_zoho,
                data_inicio=projeto.data_inicio,
                data_fim=projeto.data_fim
            )
            db.session.add(projeto_stella)
        
        # Para as atividades, vamos sempre inserir novas entradas (não verificamos duplicatas)
        if atividade_inicio:
            atividade_stella_inicio = Atividades_Stella(
                atividade_id=atividade_inicio.atividade_id,
                projeto_id=atividade_inicio.projeto_id,
                codigo_inicio=atividade_inicio.codigo_inicio,
                codigo_fim=atividade_inicio.codigo_fim,
                nome_atividade=atividade_inicio.nome_atividade,
                descricao=atividade_inicio.descricao,
                data_inicio=atividade_inicio.data_inicio,
                data_fim=atividade_inicio.data_fim,
                status=atividade_inicio.status,
                key_zoho=atividade_inicio.key_zoho
            )
            db.session.add(atividade_stella_inicio)
        
        if atividade_fim:
            atividade_stella_fim = Atividades_Stella(
                atividade_id=atividade_fim.atividade_id,
                projeto_id=atividade_fim.projeto_id,
                codigo_inicio=atividade_fim.codigo_inicio,
                codigo_fim=atividade_fim.codigo_fim,
                nome_atividade=atividade_fim.nome_atividade,
                descricao=atividade_fim.descricao,
                data_inicio=atividade_fim.data_inicio,
                data_fim=atividade_fim.data_fim,
                status=atividade_fim.status,
                key_zoho=atividade_fim.key_zoho
            )
            db.session.add(atividade_stella_fim)
        
        db.session.commit()
        
        # Retornar mensagem de sucesso
        return jsonify({"status": "success", "message": "Dados salvos com sucesso!"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
#=====================================================================================================================================================================================    
'''
@app.route('/ultimas_atividades')
def ultimas_atividades():
    atividades = Atividades_Stella.query.order_by(Atividades_Stella.id.desc()).limit(5).all()
    
    atividades_data = [{
        'id': a.id,
        'atividade_id': a.atividade_id,
        'projeto_id': a.projeto_id,
        'nome_atividade': a.nome_atividade,
        'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
        'data_fim': a.data_fim.strftime('%Y-%m-%d'),
        'status': a.status
    } for a in atividades]
    
    return jsonify(atividades_data)
'''
#=====================================================================================================================================================================================
@app.route('/grid_atividades')
def grid_atividades():
    atividades = Atividades_Stella.query.order_by(Atividades_Stella.id.desc()).limit(5).all()
    
    atividades_data = [{
        'id': a.id,
        'atividade_id': a.atividade_id,
        'projeto_id': a.projeto_id,
        'nome_atividade': a.nome_atividade,
        'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
        'data_fim': a.data_fim.strftime('%Y-%m-%d'),
        'status': a.status
    } for a in atividades]
    
    return render_template('grid_atividades.html', atividades=atividades_data)

#=====================================================================================================================================================================================
'''
# Adicione esta rota para a API (usada pelo DataTables via AJAX)
@app.route('/api/ultimas_atividades')
def api_ultimas_atividades():
    atividades = Atividades_Stella.query.order_by(Atividades_Stella.id.desc()).limit(100).all()
    
    atividades_data = [{
        'id': a.id,
        'atividade_id': a.atividade_id,
        'projeto_id': a.projeto_id,
        'nome_atividade': a.nome_atividade,
        'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
        'data_fim': a.data_fim.strftime('%Y-%m-%d'),
        'status': a.status
    } for a in atividades]
    
    return jsonify(atividades_data)
'''
#=====================================================================================================================================================================================
@app.route('/api/ultimas_atividades')
def api_ultimas_atividades():
    include_project = request.args.get('include_project', 'false').lower() == 'true'
    
    atividades = Atividades_Stella.query.order_by(Atividades_Stella.id.desc()).limit(100).all()
    
    atividades_data = []
    for a in atividades:
        atividade_dict = {
            'id': a.id,
            'atividade_id': a.atividade_id,
            'projeto_id': a.projeto_id,
            'nome_atividade': a.nome_atividade,
            'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
            'data_fim': a.data_fim.strftime('%Y-%m-%d'),
            'status': a.status,
            'key_zoho': a.key_zoho or ''
        }
        
        if include_project:
            projeto = Projetos_Stella.query.filter_by(projeto_id=a.projeto_id).first()
            if projeto:
                atividade_dict['projeto_key_zoho'] = projeto.key_zoho or ''
            else:
                # Se não encontrar na Stella, tenta na tabela principal
                projeto_principal = Projetos.query.filter_by(projeto_id=a.projeto_id).first()
                atividade_dict['projeto_key_zoho'] = projeto_principal.key_zoho if projeto_principal else ''
        
        atividades_data.append(atividade_dict)
    
    return jsonify(atividades_data)
#=====================================================================================================================================================================================

# Rota para visualizar o Gantt de uma atividade específica
@app.route('/visualizar_gantt/<int:atividade_id>')
def visualizar_gantt(atividade_id):
    atividade = Atividades_Stella.query.get(atividade_id)
    if not atividade:
        return "Atividade não encontrada", 404
    
    projeto = Projetos_Stella.query.filter_by(projeto_id=atividade.projeto_id).first()
    
    # Preparar dados para o gráfico
    dados_gantt = {
        'projeto': {
            'id': projeto.projeto_id if projeto else 'projeto-0',
            'name': f"Projeto {atividade.projeto_id}" if projeto else "Projeto Desconhecido",
            'start': projeto.data_inicio.strftime('%Y-%m-%d') if projeto else atividade.data_inicio.strftime('%Y-%m-%d'),
            'end': projeto.data_fim.strftime('%Y-%m-%d') if projeto else atividade.data_fim.strftime('%Y-%m-%d'),
        },
        'atividade': {
            'id': atividade.atividade_id,
            'name': atividade.nome_atividade,
            'start': atividade.data_inicio.strftime('%Y-%m-%d'),
            'end': atividade.data_fim.strftime('%Y-%m-%d'),
            'status': atividade.status
        }
    }
    
    return render_template('visualizar_gantt.html', dados_gantt=dados_gantt)
#=====================================================================================================================================================================================
@app.route('/gantt')
def gantt():
    try:
        projetos = Projetos.query.options(db.joinedload(Projetos.atividades)).all()
        
        # Pré-processamento dos dados
        dados_gantt = {
            'projetos': [],
            'tarefas': []
        }

        for projeto in projetos:
            # Dados do projeto
            dados_projeto = {
                'id': projeto.projeto_id or f"projeto-{projeto.id}",
                'name': projeto.nome_projeto or "Projeto sem nome",
                'start': projeto.data_inicio.strftime('%Y-%m-%d') if projeto.data_inicio else None,
                'end': projeto.data_fim.strftime('%Y-%m-%d') if projeto.data_fim else None,
                'progress': calcular_progresso(projeto.projeto_id) if projeto.projeto_id else 0
            }
            dados_gantt['projetos'].append(dados_projeto)

            # Dados das tarefas
            for atividade in projeto.atividades:
                dados_tarefa = {
                    'id': atividade.atividade_id or f"atividade-{atividade.id}",
                    'name': atividade.nome_atividade or "Atividade sem nome",
                    'start': atividade.data_inicio.strftime('%Y-%m-%d') if atividade.data_inicio else None,
                    'end': atividade.data_fim.strftime('%Y-%m-%d') if atividade.data_fim else None,
                    'progress': 100 if atividade.status == 'Concluído' else 0,
                    'status': atividade.status or "Planejado",
                    'parent': projeto.projeto_id or f"projeto-{projeto.id}"
                }
                dados_gantt['tarefas'].append(dados_tarefa)

        return render_template('gantt.html', dados_gantt=dados_gantt)

    except Exception as e:
        app.logger.error(f"Erro na rota /gantt: {str(e)}")
        return render_template('error.html', message="Erro ao carregar dados para o gráfico")


@app.route('/api/projetos')
def api_projetos():
    projetos = Projetos.query.order_by(Projetos.data_inicio).all()
    projetos_data = [{
        'id': p.id,
        'name': p.nome_projeto,
        'start': p.data_inicio.strftime('%Y-%m-%d'),
        'end': p.data_fim.strftime('%Y-%m-%d'),
        'key_zoho': p.key_zoho
    } for p in projetos]
    return jsonify(projetos_data)


# Nova rota para visualizar o Gantt com duas atividades
@app.route('/visualizar_gantt_duplo/<int:atividade_inicio_id>/<int:atividade_fim_id>')
def visualizar_gantt_duplo(atividade_inicio_id, atividade_fim_id):
    # Buscar ambas as atividades
    atividade_inicio = Atividades_Stella.query.get(atividade_inicio_id)
    atividade_fim = Atividades_Stella.query.get(atividade_fim_id)
    
    if not atividade_inicio or not atividade_fim:
        return "Atividade não encontrada", 404
    
    # Buscar projeto relacionado
    projeto = Projetos_Stella.query.filter_by(projeto_id=atividade_inicio.projeto_id).first()
    
    # Preparar dados para o gráfico
    dados_gantt = {
        'projeto': {
            'id': projeto.projeto_id if projeto else 'projeto-0',
            'name': f"Projeto {atividade_inicio.projeto_id}" if projeto else "Projeto Desconhecido",
            'start': min(
                projeto.data_inicio if projeto else atividade_inicio.data_inicio,
                atividade_inicio.data_inicio,
                atividade_fim.data_inicio
            ).strftime('%Y-%m-%d'),
            'end': max(
                projeto.data_fim if projeto else atividade_fim.data_fim,
                atividade_inicio.data_fim,
                atividade_fim.data_fim
            ).strftime('%Y-%m-%d'),
        },
        'atividades': [
            {
                'id': atividade_inicio.atividade_id,
                'name': f"[INÍCIO] {atividade_inicio.nome_atividade}",
                'start': atividade_inicio.data_inicio.strftime('%Y-%m-%d'),
                'end': atividade_inicio.data_fim.strftime('%Y-%m-%d'),
                'status': atividade_inicio.status,
                'tipo': 'inicio'
            },
            {
                'id': atividade_fim.atividade_id,
                'name': f"[FIM] {atividade_fim.nome_atividade}",
                'start': atividade_fim.data_inicio.strftime('%Y-%m-%d'),
                'end': atividade_fim.data_fim.strftime('%Y-%m-%d'),
                'status': atividade_fim.status,
                'tipo': 'fim'
            }
        ]
    }
    
    return render_template('visualizar_gantt_duplo.html', dados_gantt=dados_gantt)



'''
@app.route('/api/atividades_selecionadas')
def api_atividades_selecionadas():
    ids = request.args.get('ids', '').split(',')
    if not ids or ids[0] == '':
        return jsonify([])
    
    # Converter para inteiros e remover possíveis valores vazios
    ids = [int(id) for id in ids if id.isdigit()]
    
    atividades = Atividades_Stella.query.filter(Atividades_Stella.id.in_(ids)).all()
    
    atividades_data = [{
        'id': a.id,
        'atividade_id': a.atividade_id,
        'projeto_id': a.projeto_id,
        'nome_atividade': a.nome_atividade,
        'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
        'data_fim': a.data_fim.strftime('%Y-%m-%d'),
        'status': a.status
    } for a in atividades]
    
    return jsonify(atividades_data)
'''

# Rota existente (mantenha como está)
@app.route('/api/atividades_selecionadas')
def api_atividades_selecionadas():
    ids = request.args.get('ids', '').split(',')
    if not ids or ids[0] == '':
        return jsonify([])
    
    # Converter para inteiros e remover possíveis valores vazios
    ids = [int(id) for id in ids if id.isdigit()]
    
    atividades = Atividades_Stella.query.filter(Atividades_Stella.id.in_(ids)).all()
    
    atividades_data = [{
        'id': a.id,
        'atividade_id': a.atividade_id,
        'projeto_id': a.projeto_id,
        'nome_atividade': a.nome_atividade,
        'data_inicio': a.data_inicio.strftime('%Y-%m-%d'),
        'data_fim': a.data_fim.strftime('%Y-%m-%d'),
        'status': a.status
    } for a in atividades]
    
    return jsonify(atividades_data)

# Nova rota para visualização do Gantt múltiplo
@app.route('/visualizar_gantt_multiplo')
def visualizar_gantt_multiplo():
    return render_template('visualizar_gantt_multiplo.html')


'''
@app.route('/api/get_projeto_nome')
def api_get_projeto_nome():
    projeto_id = request.args.get('projeto_id')
    projeto = Projetos_Stella.query.filter_by(projeto_id=projeto_id).first()
    if projeto:
        return jsonify({
            'nome_projeto': projeto.nome_projeto,
            'projeto_id': projeto.projeto_id
        })
    return jsonify({'error': 'Projeto não encontrado'}), 404
'''


'''
@app.route('/api/get_projeto_nome')
def api_get_projeto_nome():
    projeto_id = request.args.get('projeto_id')
    
    # Primeiro tenta buscar na tabela Projetos_Stella
    projeto = Projetos_Stella.query.filter_by(projeto_id=projeto_id).first()
    
    # Se não encontrar, tenta na tabela Projetos
    if not projeto:
        projeto = Projetos.query.filter_by(projeto_id=projeto_id).first()
    
    if projeto:
        # Verifica se o objeto tem o atributo nome_projeto
        if hasattr(projeto, 'nome_projeto'):
            return jsonify({
                'nome_projeto': projeto.nome_projeto,
                'projeto_id': projeto.projeto_id
            })
        else:
            return jsonify({
                'nome_projeto': f"Projeto {projeto.projeto_id}",
                'projeto_id': projeto.projeto_id
            })
    
    return jsonify({
        'error': 'Projeto não encontrado',
        'projeto_id': projeto_id
    }), 404
'''

#=========================================================================================================================================================
@app.route('/api/get_projeto_nome')
def api_get_projeto_nome():
    projeto_id = request.args.get('projeto_id')
    
    # Primeiro tenta buscar na tabela Projetos (a principal)
    projeto = Projetos.query.filter_by(projeto_id=projeto_id).first()
    
    # Se não encontrar, tenta na tabela Projetos_Stella
    if not projeto:
        projeto = Projetos_Stella.query.filter_by(projeto_id=projeto_id).first()
    
    if projeto:
        # Verifica se o objeto tem o atributo nome_projeto
        if hasattr(projeto, 'nome_projeto') and projeto.nome_projeto:
            return jsonify({
                'nome_projeto': projeto.nome_projeto,
                'projeto_id': projeto.projeto_id
            })
    
    # Se não encontrou em nenhuma tabela ou não tem nome
    return jsonify({
        'error': 'Nome do projeto não encontrado',
        'projeto_id': projeto_id
    }), 404
#=========================================================================================================================================================

@app.route('/api/tarefas/<int:projeto_id>')
def api_tarefas(projeto_id):
    tarefas = Atividades.query.filter_by(projeto_id=projeto_id).order_by(Atividades.data_inicio).all()
    tarefas_data = [{
        'id': t.id,
        'name': t.nome_atividade,
        'start': t.data_inicio.strftime('%Y-%m-%d'),
        'end': t.data_fim.strftime('%Y-%m-%d'),
        'status': t.status,
        'projeto_id': t.projeto_id
    } for t in tarefas]
    return jsonify(tarefas_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

