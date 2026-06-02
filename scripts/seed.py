"""
Script de semillado (seeding) para poblar la base de datos con datos de prueba iniciales.
Incluye la creación de usuarios con diferentes roles, cursos y solicitudes de inscripción.
"""

import os
import sys
import bcrypt
from datetime import date, timedelta

# Añade el directorio src al path de búsqueda de módulos.
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.application import Application
from app.utils.enums import Role, ApplicationStatus

def get_password_hash(password: str) -> str:
    """
    Genera un hash bcrypt a partir de una contraseña de texto plano.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def seed_data():
    """
    Inserta datos ficticios de prueba en la base de datos si esta se encuentra vacía.
    """
    db = SessionLocal()
    
    try:
        # Comprueba si ya existen usuarios registrados para evitar la duplicación de datos.
        if db.query(User).count() > 0:
            print("Database already seeded!")
            return
            
        print("Seeding database...")
        
        # 1. Crea usuarios administradores por defecto.
        admin1 = User(name="Admin One", email="admin1@courseflow.com", password=get_password_hash("admin123"), role=Role.ADMIN)
        admin2 = User(name="Super Admin", email="superadmin@courseflow.com", password=get_password_hash("superadmin123"), role=Role.SUPERADMIN)
        
        # 2. Crea usuarios estándar de prueba.
        users = []
        for i in range(1, 6):
            user = User(
                name=f"User {i}",
                email=f"user{i}@courseflow.com",
                password=get_password_hash("user123"),
                role=Role.USER
            )
            users.append(user)
            
        db.add_all([admin1, admin2] + users)
        db.commit()
        
        # 3. Crea los cursos iniciales en la base de datos.
        course1 = Course(
            name="Python Básico",
            description="Aprende los fundamentos de Python",
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=40),
            capacity=20,
            is_active=True
        )
        course2 = Course(
            name="Desarrollo Web con FastAPI",
            description="Crea APIs robustas y rápidas",
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=60),
            capacity=15,
            is_active=True
        )
        course3 = Course(
            name="Bases de Datos Avanzadas",
            description="SQL y optimización",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=90),
            capacity=10,
            is_active=True
        )
        db.add_all([course1, course2, course3])
        db.commit()
        
        # 4. Crea solicitudes de inscripción iniciales para los cursos.
        applications = [
            Application(user_id=users[0].id, course_id=course1.id, status=ApplicationStatus.PENDING),
            Application(user_id=users[0].id, course_id=course2.id, status=ApplicationStatus.ACCEPTED),
            Application(user_id=users[1].id, course_id=course1.id, status=ApplicationStatus.PENDING),
            Application(user_id=users[1].id, course_id=course3.id, status=ApplicationStatus.REJECTED),
            Application(user_id=users[2].id, course_id=course2.id, status=ApplicationStatus.ACCEPTED),
            Application(user_id=users[2].id, course_id=course3.id, status=ApplicationStatus.PENDING),
            Application(user_id=users[3].id, course_id=course1.id, status=ApplicationStatus.CANCELLED),
            Application(user_id=users[3].id, course_id=course2.id, status=ApplicationStatus.PENDING),
            Application(user_id=users[4].id, course_id=course1.id, status=ApplicationStatus.PENDING),
            Application(user_id=users[4].id, course_id=course3.id, status=ApplicationStatus.ACCEPTED),
        ]
        
        db.add_all(applications)
        db.commit()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
