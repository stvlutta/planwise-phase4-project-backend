from flask import Flask, request, jsonify
from flask_cors import CORS
# Temporarily remove Flask-Migrate to avoid SQLAlchemy compatibility issues
# from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Task, Project, ProjectCollaborator, bcrypt
from config import Config
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.json.compact = False

# Handle PostgreSQL URL format for Render
database_url = app.config['SQLALCHEMY_DATABASE_URI']
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
# Temporarily remove migrate
# migrate = Migrate(app, db)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize database tables for serverless deployment
def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            return True
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False

# Initialize database for serverless deployment
try:
    init_db()
except Exception as e:
    print(f"Database initialization failed: {e}")

# Health check routes
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'message': 'PlanWise Backend API is running!', 'status': 'healthy'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

# Authentication routes
@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Validation
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    try:
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

# User routes
@app.route('/users', methods=['GET'])
@jwt_required()
def users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def user_by_id(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(user.to_dict())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(user.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204

# Task routes
@app.route('/tasks', methods=['GET', 'POST'])
@jwt_required()
def tasks():
    current_user_id = int(get_jwt_identity())
    
    if request.method == 'GET':
        # Get tasks assigned to current user
        tasks = Task.query.filter_by(user_id=current_user_id).all()
        return jsonify([task.to_dict() for task in tasks])
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            task = Task(
                title=data['title'],
                description=data.get('description', ''),
                status=data.get('status', 'pending'),
                priority=data.get('priority', 'medium'),
                user_id=current_user_id,  # Assign to current user
                project_id=data.get('project_id'),
                due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
            )
            db.session.add(task)
            db.session.commit()
            return jsonify(task.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/tasks/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def task_by_id(id):
    current_user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(id)
    
    # Check if user owns this task
    if task.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'GET':
        return jsonify(task.to_dict())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for key, value in data.items():
                if key == 'due_date' and value:
                    setattr(task, key, datetime.fromisoformat(value))
                elif hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(task.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204

# Project routes
@app.route('/projects', methods=['GET', 'POST'])
@jwt_required()
def projects():
    current_user_id = int(get_jwt_identity())
    
    if request.method == 'GET':
        # Get projects owned by current user or where they are a collaborator
        owned_projects = Project.query.filter_by(owner_id=current_user_id).all()
        collaborated_projects = Project.query.join(ProjectCollaborator).filter_by(user_id=current_user_id).all()
        
        # Combine and remove duplicates
        all_projects = list(set(owned_projects + collaborated_projects))
        return jsonify([project.to_dict() for project in all_projects])
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            project = Project(
                title=data['title'],
                description=data.get('description', ''),
                owner_id=current_user_id  # Use current user as owner
            )
            db.session.add(project)
            db.session.commit()
            return jsonify(project.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/projects/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def project_by_id(id):
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(id)
    
    # Check if user has access to this project (owner or collaborator)
    is_owner = project.owner_id == current_user_id
    is_collaborator = ProjectCollaborator.query.filter_by(user_id=current_user_id, project_id=id).first() is not None
    
    if not (is_owner or is_collaborator):
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'GET':
        return jsonify(project.to_dict())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for key, value in data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(project.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return '', 204

# Project collaborator routes
@app.route('/project-collaborators', methods=['GET', 'POST'])
@jwt_required()
def project_collaborators():
    if request.method == 'GET':
        collaborators = ProjectCollaborator.query.all()
        return jsonify([collab.to_dict() for collab in collaborators])
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            collaborator = ProjectCollaborator(
                user_id=data['user_id'],
                project_id=data['project_id'],
                role=data['role']
            )
            db.session.add(collaborator)
            db.session.commit()
            return jsonify(collaborator.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/project-collaborators/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def project_collaborator_by_id(id):
    collaborator = ProjectCollaborator.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(collaborator.to_dict())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for key, value in data.items():
                if hasattr(collaborator, key):
                    setattr(collaborator, key, value)
            collaborator.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(collaborator.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(collaborator)
        db.session.commit()
        return '', 204


# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=False)
