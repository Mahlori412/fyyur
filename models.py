from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    genres = db.Column(db.String(),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_description = db.Column(db.String(),nullable=True)
    relations = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state}>'

   

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(),nullable = False)
    image_link = db.Column(db.String(),nullable = False)
    facebook_link = db.Column(db.String(),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_description = db.Column(db.String(),nullable = False)
    seeking_venue = db.Column(db.Boolean, default=False)
    relations = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime())