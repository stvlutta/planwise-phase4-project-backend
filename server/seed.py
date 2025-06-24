from app import app
from models import db, User, Task, Project, ProjectCollaborator
from datetime import datetime, timedelta

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        user1 = User(username='steve', email='steve@example.com')
        user1.set_password('password123')
        
        user2 = User(username='luke', email='luke@example.com')
        user2.set_password('password123')
        
        user3 = User(username='mudalib', email='mudalib@example.com')
        user3.set_password('password123')
        
        user4 = User(username='claire', email='claire@example.com')
        user4.set_password('password123')
        
        user5 = User(username='dylan', email='dylan@example.com')
        user5.set_password('password123')
        
        db.session.add_all([user1, user2, user3, user4, user5])
        db.session.commit()
        
        # Create projects
        project1 = Project(
            title='Website Redesign',
            description='Redesign the company website with modern UI/UX',
            owner_id=user1.id
        )
        
        project2 = Project(
            title='Mobile App Development',
            description='Develop a mobile app for iOS and Android',
            owner_id=user2.id
        )
        
        project3 = Project(
            title='Database Migration',
            description='Migrate from MySQL to PostgreSQL',
            owner_id=user1.id
        )
        
        db.session.add_all([project1, project2, project3])
        db.session.commit()
        
        # Create project collaborators
        collab1 = ProjectCollaborator(user_id=user2.id, project_id=project1.id, role='member')
        collab2 = ProjectCollaborator(user_id=user3.id, project_id=project1.id, role='viewer')
        collab3 = ProjectCollaborator(user_id=user4.id, project_id=project1.id, role='member')
        collab4 = ProjectCollaborator(user_id=user1.id, project_id=project2.id, role='member')
        collab5 = ProjectCollaborator(user_id=user3.id, project_id=project2.id, role='member')
        collab6 = ProjectCollaborator(user_id=user5.id, project_id=project2.id, role='viewer')
        collab7 = ProjectCollaborator(user_id=user2.id, project_id=project3.id, role='member')
        collab8 = ProjectCollaborator(user_id=user4.id, project_id=project3.id, role='viewer')
        
        db.session.add_all([collab1, collab2, collab3, collab4, collab5, collab6, collab7, collab8])
        db.session.commit()
        
        # Create tasks
        tasks = [
            Task(
                title='Design homepage mockup',
                description='Create wireframes and mockups for the new homepage',
                status='in_progress',
                priority='high',
                user_id=user1.id,
                project_id=project1.id,
                due_date=datetime.utcnow() + timedelta(days=7)
            ),
            Task(
                title='Implement user authentication',
                description='Add login and registration functionality',
                status='pending',
                priority='high',
                user_id=user2.id,
                project_id=project1.id,
                due_date=datetime.utcnow() + timedelta(days=10)
            ),
            Task(
                title='Write API documentation',
                description='Document all API endpoints with examples',
                status='completed',
                priority='medium',
                user_id=user3.id,
                project_id=project1.id
            ),
            Task(
                title='Set up mobile development environment',
                description='Install and configure React Native development tools',
                status='completed',
                priority='high',
                user_id=user2.id,
                project_id=project2.id
            ),
            Task(
                title='Design mobile app UI',
                description='Create UI mockups for all app screens',
                status='in_progress',
                priority='medium',
                user_id=user4.id,
                project_id=project2.id,
                due_date=datetime.utcnow() + timedelta(days=14)
            ),
            Task(
                title='Implement push notifications',
                description='Add push notification functionality to mobile app',
                status='pending',
                priority='low',
                user_id=user5.id,
                project_id=project2.id,
                due_date=datetime.utcnow() + timedelta(days=21)
            ),
            Task(
                title='Backup current database',
                description='Create full backup of MySQL database before migration',
                status='completed',
                priority='high',
                user_id=user1.id,
                project_id=project3.id
            ),
            Task(
                title='Set up PostgreSQL server',
                description='Install and configure PostgreSQL on production server',
                status='in_progress',
                priority='high',
                user_id=user1.id,
                project_id=project3.id,
                due_date=datetime.utcnow() + timedelta(days=3)
            ),
            Task(
                title='Buy groceries',
                description='Get ingredients for dinner tonight',
                status='pending',
                priority='medium',
                user_id=user4.id,
                due_date=datetime.utcnow() + timedelta(days=1)
            ),
            Task(
                title='Schedule dentist appointment',
                description='Call dentist office to schedule cleaning',
                status='pending',
                priority='low',
                user_id=user5.id
            )
        ]
        
        db.session.add_all(tasks)
        db.session.commit()
        
        print("Database seeded successfully!")
        print(f"Created {len([user1, user2, user3, user4, user5])} users")
        print(f"Created {len([project1, project2, project3])} projects")
        print(f"Created {len([collab1, collab2, collab3, collab4, collab5, collab6, collab7, collab8])} project collaborations")
        print(f"Created {len(tasks)} tasks")

if __name__ == '__main__':
    seed_data()