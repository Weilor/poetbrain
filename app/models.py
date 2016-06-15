#!/usr/bin/env python
# encoding=utf-8

from datetime import datetime
from app import db, lm
from flask_login import UserMixin, current_app, AnonymousUserMixin
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serialization
import hashlib


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    """
    用户角色模型
    id          :key键
    name        :角色名称
    default     :默认角色控制
    permission  :角色权限
    users       :用户的反向调用
    """
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=True, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref="role", lazy='dynamic')

    @staticmethod
    def insert_roles():
        """
        用于向数据库自动插入角色
        """
        roles = {
            "Admin": [
                Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS |
                Permission.ADMINISTER, False
            ],
            "User": [
                Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, False
            ],
            "Visitor": [
                Permission.FOLLOW, True
            ]
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][1]
            role.permissions = roles[r][0]
            db.session.add(role)
            db.session.commit()


class User(UserMixin, db.Model):
    """
    用户的数据库模型
    继承了两个类，其中UserMixin是Flask-login要求的用户类，用于执行各类登录登出操作
    id            :key值
    username      :用户名
    email         :注册邮箱
    location      :地址
    about_me      :自我简介
    password_hash :密码哈希值
    role_id       :角色ID，外键
    confirmed     :邮箱是否验证
    last_seen     :上次登录时间
    member_since  :注册时间
    article       :用户文章，外键反向回指
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    articles = db.relationship('Article', backref="author", lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(name="Admin").first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        """
        密码设为property，不可读取，在数据库中以hash值存储，增加安全性
        """
        raise AttributeError("password can not be read!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expiration=3600):
        s = Serialization(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'Confirmed': self.id})

    def check_token(self, token):
        s = Serialization(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        else:
            if data.get('Confirmed') != self.id:
                return False
            self.confirmed = True
            db.session.add(self)
            return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gavatar(self, size):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://cn.gravatar.com/avatar'
        hash_id = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash_id, size=size, default='identicon', rating='g')


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    prototype_id = db.Column(db.Integer, db.ForeignKey("prototypes.id"))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    rate = db.Column(db.Float)


class Prototype(db.Model):
    __tablename__ = "prototypes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_hash = db.Column(db.String(128), unique=True, index=True)
    dynasty = db.Column(db.String(64))
    author = db.Column(db.String(64), index=True)
    articles = db.relationship('Article', backref="prototype", lazy='dynamic')

    @staticmethod
    def add_prototype(title, dynasty, author, body):
        if Prototype.query.filter_by(body_hash=hashlib.md5(body).hexdigest()).first() is not None:
            return False
        prototype = Prototype(title=title, dynasty=dynasty, author=author,
                              body=body, body_hash=hashlib.md5(body).hexdigest())
        db.session.add(prototype)
        db.session.commit()
        return True

    @staticmethod
    def is_prototype_exist(author_or_title):
        pro_list = Prototype.query.filter_by(title=author_or_title).all()
        if (pro_list is not None) and (len(pro_list) != 0):
            return pro_list
        pro_list = Prototype.query.filter_by(author=author_or_title).all()
        if (pro_list is not None) and (len(pro_list) != 0):
            return pro_list


class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def can(permissions):
        return False

    @staticmethod
    def is_administrator():
        return False

lm.anonymous_user = AnonymousUser


class Permission:
    FOLLOW = 0x01                  #关注其他用户
    COMMENT = 0x02                 #发布评论
    WRITE_ARTICLES = 0x04          #发布文章
    MODERATE_COMMENTS = 0x08       #审查评论
    ADMINISTER = 0x80              #管理网站
