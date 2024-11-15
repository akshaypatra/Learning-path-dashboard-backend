from django.contrib.auth.hashers import make_password
from db_connection import db


class BaseUser:
    def __init__(self, role, name, email, password):
        self.role = role
        self.name = name
        self.email = email
        self.password = make_password(password) if not password.startswith('pbkdf2') else password

    def save(self):
        # Insert or update the user in the MongoDB collection
        user_collection = db["users"]
        user_data = {
            "role": self.role,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }
        # Insert or update (upsert)
        user_collection.update_one({"email": self.email}, {"$set": user_data}, upsert=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Teacher(BaseUser):
    def __init__(self, name, email, password, employeeID):
        super().__init__("teacher", name, email, password)
        self.employeeID = employeeID

    def save(self):
        # Check if employeeID is unique
        if db["teachers"].find_one({"employeeID": self.employeeID, "email": {"$ne": self.email}}):
            raise ValueError(f"Teacher with employee ID {self.employeeID} already exists.")

        # Save the Teacher document to the MongoDB collection
        teacher_collection = db["teachers"]
        teacher_data = {
            "role": self.role,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "employeeID": self.employeeID
        }
        teacher_collection.update_one({"email": self.email}, {"$set": teacher_data}, upsert=True)

    def __str__(self):
        return f"{self.name} - {self.employeeID}"


class Student(BaseUser):
    def __init__(self, name, email, password, enrollmentNumber, department):
        super().__init__("student", name, email, password)
        self.enrollmentNumber = enrollmentNumber
        self.department = department

    def save(self):
        # Check if enrollmentNumber is unique
        if db["students"].find_one({"enrollmentNumber": self.enrollmentNumber, "email": {"$ne": self.email}}):
            raise ValueError(f"Student with enrollment number {self.enrollmentNumber} already exists.")

        # Save the Student document to the MongoDB collection
        student_collection = db["students"]
        student_data = {
            "role": self.role,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "enrollmentNumber": self.enrollmentNumber,
            "department": self.department
        }
        student_collection.update_one({"email": self.email}, {"$set": student_data}, upsert=True)

    def __str__(self):
        return f"{self.name} - {self.enrollmentNumber}"
