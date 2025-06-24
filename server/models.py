from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    owned_projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    project_collaborations = db.relationship('ProjectCollaborator', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-password_hash', '-tasks.user', '-owned_projects.owner', '-project_collaborations.user', '-tasks.project.owner', '-owned_projects.tasks.user')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model, SerializerMixin):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    collaborators = db.relationship('ProjectCollaborator', backref='project', lazy=True, cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-owner.owned_projects', '-tasks.project', '-collaborators.project', '-owner.tasks', '-tasks.user.owned_projects')
    
    def __repr__(self):
        return f'<Project {self.title}>'

class Task(db.Model, SerializerMixin):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    due_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Serialization rules
    serialize_rules = ('-user.tasks', '-project.tasks', '-user.owned_projects', '-project.owner.tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'

class ProjectCollaborator(db.Model, SerializerMixin):
    __tablename__ = 'project_collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, member, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate collaborations
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project'),)
    
    # Serialization rules
    serialize_rules = ('-user.project_collaborations', '-project.collaborators', '-user.tasks', '-project.tasks', '-user.owned_projects', '-project.owner')
    
    def __repr__(self):
        return f'<ProjectCollaborator {self.user.username} - {self.project.title} ({self.role})>'