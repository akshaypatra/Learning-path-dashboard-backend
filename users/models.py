from django.contrib.auth.hashers import make_password, check_password
from db_connection import db
# from rest_framework_simplejwt.tokens import RefreshToken
from bson import ObjectId
from django.conf import settings
import datetime
import jwt

SECRET_KEY = settings.SECRET_KEY  # Ensure it's set in settings.py
ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 24

class BaseUser:
    def __init__(self, role, name, email, password, user_id=None):
        self.role = role
        self.name = name
        self.email = email
        self.password = make_password(password) if not password.startswith('pbkdf2') else password
        self.user_id = user_id  # Ensure user_id is assigned here

    @property
    def id(self):
        return str(self.user_id)  # MongoDB `_id` field as `id`

    def save(self):
        """Insert or update the user in the MongoDB collection."""
        user_collection = db["users"]
        user_data = {
            "role": self.role,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }
        # Insert or update (upsert) the user in the collection
        user_collection.update_one({"email": self.email}, {"$set": user_data}, upsert=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
    
    # def generate_jwt_token(self):
    #     """Generate JWT token for authentication."""
    #     if not self.user_id:
    #         raise ValueError("User must have a valid ID for token generation.")
        
    #     refresh = RefreshToken.for_user(self)  # Now this will work as self.user_id is set
    #     return {
    #         "refresh": str(refresh),
    #         "access": str(refresh.access_token),
    #     }

    def generate_jwt_token(self):
        """Generate JWT token manually."""
        payload = {
            "user_id": self.id,
            "email": self.email,
            "role": self.role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS),
            "iat": datetime.datetime.now(datetime.timezone.utc)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "access": token
        }

    @staticmethod
    def authenticate(email, password):
        """Authenticate user based on email and password."""
        # First check in the general users collection
        user_collection = db["users"]
        user = user_collection.find_one({"email": email})


        if not user:
            # If not found in the general users collection, check the teachers collection
            user = db["teachers"].find_one({"email": email})

        if not user:
            # If not found in the teachers collection, check the students collection
            user = db["students"].find_one({"email": email})

        if user and check_password(password, user["password"]):
            
            user_id = str(user["_id"]) if isinstance(user["_id"], ObjectId) else user["_id"]

            # Create the appropriate user object based on the collection
            if "employeeID" in user:
                # This is a teacher
                user_instance = Teacher(
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                    user_id=user_id,  
                    employeeID=user.get("employeeID", None)
                )
            elif "enrollmentNumber" in user:
                # This is a student
                user_instance = Student(
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                    user_id=user_id,  
                    enrollmentNumber=user["enrollmentNumber"],
                    department=user["department"]
                )
            else:
                # This is a general user
                user_instance = BaseUser(
                    role=user["role"],
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                    user_id=user_id  
                )
            # Return the JWT token
            return user_instance.generate_jwt_token()

        # If no user found or password doesn't match
        return None
    
    @staticmethod
    def decode_jwt_token(token):
        """Decode and verify the JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload  # Contains user_id, email, role
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}

class Teacher(BaseUser):
    def __init__(self, name, email, password, employeeID):
        # Initialize Teacher-specific attributes
        super().__init__("teacher", name, email, password)
        self.employeeID = employeeID

    def save(self):
        """Save the teacher's data after ensuring employeeID is unique."""
        # Check if the employee ID already exists in the collection
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
    def __init__(self, name, email, password, enrollmentNumber, department, class_code=None):
        # Initialize Student-specific attributes
        super().__init__("student", name, email, password)
        self.enrollmentNumber = enrollmentNumber
        self.department = department
        self.class_code = class_code

    def save(self):
        """Save the student's data after ensuring enrollmentNumber is unique."""
        # Check if the enrollment number already exists in the collection
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
            "department": self.department,
            "class_code": self.class_code
        }
        student_collection.update_one({"email": self.email}, {"$set": student_data}, upsert=True)

    def update_class_code(self, new_class_code):
        class_exists = db["learning_paths"].find_one({"classID": new_class_code})
        if not class_exists:
            raise ValueError(f"Class with code {new_class_code} does not exist.")

        self.classID = new_class_code  
        db["students"].update_one({"email": self.email}, {"$set": {"classID": self.classID}})
        return f"Class code updated to {new_class_code}"

    def __str__(self):
        return f"{self.name} - {self.enrollmentNumber}"
