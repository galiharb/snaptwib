from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), primary_key=True ,unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Twibbon(db.Model):
    __tablename__ = 'twibbon'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    id_twibbon = db.Column(db.String(120), nullable=False)
    title_twibbon = db.Column(db.String(255), nullable=False)
    path_twibbon = db.Column(db.String(255), nullable=False)
    tanggal_twibbon = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Twibbon %r>' % self.id
    
    def to_dict(self):
        return {
            'id_twibbon': self.id_twibbon,
            'title_twibbon': self.title_twibbon,
            'username': self.username,
            'path_twibbon' : self.path_twibbon
        }