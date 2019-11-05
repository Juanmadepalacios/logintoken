from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), nullable =False)
    password = db.Column(db.String(255), nullable =False)
    mail = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return '<User %r>' % self.username, self.password, self.mail

    def serialize(self):
        return {
            "username": self.username,
            "password": self.password,
            "mail": self.mail,
        }

