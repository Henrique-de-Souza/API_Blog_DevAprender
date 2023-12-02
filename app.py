from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Postagem, Autor, app, db
import json 
import jwt
from datetime import datetime, timedelta
from functools import wraps


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
    
        # verificar se um token foi enviado:
        if 'x-access-token' in request.headers:

            # se existir um token, extrair a informação:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído'}, 401)
        
        # Se existir um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


# Rotas para autentificação ------------------------------------------------------------------------------

# 1 - Rota de login
@app.route('/login')
def login():

    # extrair informações de autenficiação:
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório'})

    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta
        (minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token})
    
    # caso o login seja inválido:
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório'})
    


# ROTAS PARA OS VERBOS HTTP - GET, POST, PUT e DELETE -----------------------------------------------------

# 1 - Rota padrão - http://localhost:5000/
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):

     # extraindo todas as postagens do banco de dados:
    postagens = Postagem.query.all()

    # exibindo todas as postagens extraídas:
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
    lista_de_postagens.append(postagem_atual)

    return jsonify({f'postagens': lista_de_postagens})



# 2 - obter postagem por id  GET - http://localhost:5000/postagem/ (digite o id)
@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_id(autor, id_postagem):

    # procurando postagens pelo seu id:
    postagem = Postagem.query.filter_by(id_postagens=id_postagem).first()

    postagem_atual = {}

    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass

    try:
        postagem_atual['id_autor'] = postagem.titulo
    except:
        pass

    return jsonify({'postagens': postagem_atual})



# 3 - Criar nova postagem POST - http://localhost:5000/postagem/
@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):

    # tratando a requisição do usuário para incluir um novo post:
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'],
        id_autor=nova_postagem['id_autor']
    )

    # salvando atualizações
    db.session.add(postagem)
    db.session.commit()

    # retornar uma mensagem de sucesso:
    return jsonify({'mensagem': 'Postagem criada com sucesso'}, 200)



# 4-  Alterar uma postagem PUT - http://localhost:5000/postagem/(digite o id)
@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):

    # extrair informações que foram enviadas pela requisição:
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem= id_postagem).first()

    if not postagem:
        return jsonify({'mensagem': 'Postagem não encontrada'})
     
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
     
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass
     
     # salvando atualizações
    db.session.commit()

    # retornando mensagem de sucesso:
    return jsonify({'mensagem': 'Postagem alterada com sucesso'}, 200)



# 5-  Excluir uma postagem DELETE - http://localhost:5000/postagem/ (digite o id)
@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor, id_postagem):

    # verificar se existe um autor para excluir:
    postagem_a_ser_excluida = Postagem.query.filter_by(id_postagem= id_postagem).fisrt()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma postagem com este id '})

    # caso exista uma postagem, basta excluí-la:
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluída com sucesso'}, 200)



# Construir as rotas para encontrar autores: ----------------------------------------------------------------

# 1 - obter todos os autores GET - http://localhost:5000/autores
@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):

    # extraindo todos os autores do banco de dados:
    autores = Autor.query.all()

    # exibindo todos os autores extraídos:
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['Nome'] = autor.nome
        autor_atual['email'] = autor.email

        lista_de_autores.append(autor_atual)
    
    return jsonify({'autores': lista_de_autores})



# 2 - obter autores por id GET id - http://localhost:5000/autores/ (digite o id)
@app.route('/autor/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autores_por_id(autor, id_autor):

    # Procurando autores pelo seu id:
    autor = Autor.query.filter_by(id_autor = id_autor).first()
    if not autor:
        return jsonify({'autor': 'Autor não encontrado'})
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['Nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify({'autor': autor_atual})



# 3- Incluir um novo autor POST - http://localhost:5000/autores
@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):

    # Tratando a requisição de incluir um novo autor:
    novo_autor = request.get_json()
    autor = Autor(
        nome=['nome'],
        senha=['senha'],
        email=['email']
    )
    # salvando esse novo autor de fato.
    db.session.add(autor)
    db.session.commit()

    # Retornando a requisição ao usuário:
    return jsonify({'mensagem': 'Usuário criado com sucesso'}, 200)



# 4- Alterar um autor existente PUT - http://localhost:5000/autores/ (digite o id)
@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def autor_alterado(autor, id_autor):
    
    # extrair informações que foram enviadas pela requisição:
    autor_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor= id_autor).first()

    if not autor:
        return jsonify({'Mensagem': 'Este usuário não foi encontrado'})
    
    # Para conseguir alterar informações de autor, é necessário primeiramente
    # verificar se essas, foram passadas dentro da requisição:
    try:
        autor.nome = autor_a_alterar['nome']
    except:
        pass

    try:
        autor.email = autor_a_alterar['email']
    except:
        pass

    try:
        autor.senha = autor_a_alterar['senha']
    except:
        pass


    # salvando alterações:
    db.session.commit()

    # Retornando a resposta da requisição ao usuário:
    return jsonify({'mensagem': 'usuário alterado com sucesso'}, 200)
    
    

# 5 - Excluir um autor existente DELETE - http://localhost:5000/autores/ (digite o id)
@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    
    # verificar se existe um autor para excluir:
    autor_existente = Autor.query.filter_by(id_autor= id_autor).first()
    if not autor_existente:
        return jsonify({'mensagem': 'Autor não encontrado'})
    
    # caso ele exista, basta deletá-lo:
    db.session.delete(autor_existente)

    # salvando atualizações:
    db.session.commit()

    # Retornando mensagem de sucesso:
    return jsonify({'mensagem': 'Autor excluído com sucesso'}, 200)


# Sintaxe para rodar localmente a API.
app.run(port=5000, host='localhost', debug=True)
