from models.student import StudentModel
from models.category import CategoryModel
from models.category_student_self_description import CategoryStudentSelfDescriptionModel
from db_app import db

def configure_relationships():
    # Define the relationships now that all models are loaded
    StudentModel.self_descriptions = db.relationship('CategoryStudentSelfDescriptionModel', back_populates='student', lazy='dynamic')
    CategoryModel.descriptions = db.relationship('CategoryStudentSelfDescriptionModel', back_populates='category', lazy='dynamic')
    CategoryStudentSelfDescriptionModel.student = db.relationship('StudentModel', back_populates='self_descriptions')
    CategoryStudentSelfDescriptionModel.category = db.relationship('CategoryModel', back_populates='descriptions')
