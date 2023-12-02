from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Criar uma API flask
app = Flask(__name__)

# Definir informações importantes de configurações do banco de dados
app.config['SECRET_KEY'] = 'FDSAasdf260454*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

# Criar uma instancia de SQLAlchemy
db = SQLAlchemy(app)
db:SQLAlchemy

# Definir a estrutura da tabela de postagens:
# Essa tabela terá colunas e linhas;
# Será identificada por id, titulo e autor.

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    título = db.Column(db.String)

    # Criar uma relação entre autor e postagem:
    # usando uma chave estrangeira, referênciando uma outra tabela
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))



# Definir a estrutura da tabela de autores:
# Essa tabela também terá colunas e linhas;
# Será identificada por: id, nome, email, senha, admin, postagens

class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)

    # Criar uma relação entre o autor e as postagens,
    # para ter acesso, as postagens por autor.
    postagens = db.relationship('Postagem')

# Criar o banco de dados.
def iniciar_banco_de_dados():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Criar usuários administradores
        autor = Autor(nome='Henrique', email='enriquedesuu@gmail,com', senha='123456', admin=True)
        db.session.add(autor)
        db.session.commit()


# Criar uma condição para que a função iniciar_banco_de_dados, só seja executada, 
# quando e se for chamada, para que não tenhamos nosso banco de dados, apagado 
# e recriado a cada momento em que fazemos uso da classe db. 
if __name__ == '__main__':
    iniciar_banco_de_dados()