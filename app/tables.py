import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = sa.Column(sa.Integer, primary_key=True)
    user_ids = sa.Column(sa.String)
    creation_date = sa.Column(sa.Date)
    last_used_date = sa.Column(sa.Date)
    status = sa.Column(sa.String)
    header = sa.Column(sa.String)
    text = sa.Column(sa.String)
    votes = sa.Column(sa.Integer)
    summary_mark = sa.Column(sa.Numeric)
    tags = sa.Column(sa.String)



class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.Text, unique=True)
    username = sa.Column(sa.Text, unique=True)
    password = sa.Column(sa.Text)
    role = sa.Column(sa.Text)
    bannedUntil = sa.Column(sa.Text)

class Comment(Base):
    __tablename__ = "comments"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    article_id = sa.Column(sa.Integer, sa.ForeignKey('articles.id'))
    text = sa.Column(sa.String)
    status = sa.Column(sa.Text)

class Mark(Base):
    __tablename__ = "marks"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    article_id = sa.Column(sa.Integer, sa.ForeignKey('articles.id'))
    mark = sa.Column(sa.Integer)

class Tag(Base):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    tag = sa.Column(sa.Text, unique=True)