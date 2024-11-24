from django.db import models
import bcrypt
import re
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Value
from django.db.models.functions import Concat

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors["first_name"] = "First name should be at least 2 characters, no special characters allowed."
            return errors
        if len(postData['last_name']) < 2:
            errors["last_name"] = "Last name should be at least 2 characters, no special characters allowed."
            return errors
        if len(postData['email']) < 1:
            errors["email"] = "Please provide an email address."
            return errors
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "The email address you've entered is invalid."
            return errors
        existing_email = User.objects.filter(email=postData['email']).exclude(id=postData.get('id'))
        if existing_email.exists():
            errors["email"] = "This email address was already used before. Please login or use a different email address."
            return errors
        if len(postData['password']) < 8:
            errors["password"] = "Password should be at least 8 characters."
            return errors
        if postData['password'] != postData['passwordconfirmation']:
            errors["passwordconfirmation"] = "Passwords do not match."
            return errors
        if not postData['date_of_birth']:
            errors["date_of_birth"] = "Please select your date of birth first."
            return errors
        date_of_birth = datetime.strptime(postData['date_of_birth'], "%Y-%m-%d").date()
        if date_of_birth > datetime.today().date():
            errors["date_of_birth"] = "Please select a valid date of birth, as date of birth cannot be in the future."
            return errors
        if not postData.get('gender'):
            errors["gender"] = "Please choose a gender first."
            return errors
        return errors
    def login_validator(self, postData):
        errors = {}
        if len(postData['email']) < 1:
            errors["email"] = "Please provide an email address."
            return errors
        if len(postData['password']) < 1:
            errors["password"] = "Please provide a password."
            return errors
        elif not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "The email address you've entered is invalid."
            return errors
        else:
            user = User.objects.filter(email=postData['email']).first()
            if not user:
                errors["email"] = "No user account with this email address was found."
                return errors
            else:
                if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                    errors["password"] = "Incorrect password."
                    return errors
        return errors
    def update_data_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors["first_name"] = "First name should be at least 2 characters, no special characters allowed."
            return errors
        if len(postData['last_name']) < 2:
            errors["last_name"] = "Last name should be at least 2 characters, no special characters allowed."
            return errors
        if len(postData['email']) < 1:
            errors["email"] = "Please provide an email address."
            return errors
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "The email address you've entered is invalid."
            return errors
        user = postData['user']
        existing_email = User.objects.filter(email=postData['email']).exclude(id=postData.get('id'))
        if existing_email.exists():
            errors["email"] = "This email address was already used before. Please use a different email address."
            return errors
        if len(postData['current_password']) > 1 or len(postData['new_password']) > 1 or len(postData['confirm_new_password']) > 1:
            if len(postData['current_password']) < 8:
                errors["current_password"] = "Please enter your current password."
                return errors
            if len(postData['new_password']) < 8:
                errors["new_password"] = "Your new password should at least be 8 characters."
                return errors
            if postData['new_password'] != postData['confirm_new_password']:
                errors["new_password"] = "New password confirmation does not match."
                return errors
            if not bcrypt.checkpw(postData['current_password'].encode(), user.password.encode()):
                errors["current_password"] = "Incorrect current password."
                return errors
        return errors
    def create_user(self, postData):
        from social_app.models import PersonalDetails
        hashed_password = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(first_name=postData['first_name'], last_name=postData['last_name'], email=postData['email'], password=hashed_password, date_of_birth=postData['date_of_birth'], gender=postData['gender'])
        PersonalDetails.objects.create_personal_details_record(user)
        return user
    def get_user(self, id):
        return User.objects.get(id=id)
    def get_full_name(self, user):
        return f"{user.first_name} {user.last_name}"
    def search(self, search):
        return self.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(full_name__icontains=search)
        )
    def update_user_activity(self, user):
        user.last_activity = timezone.now()
        user.save()
    def is_user_online(self, user):
        now = timezone.now()
        if user.last_activity > now - timedelta(minutes=5):
            return True
        return False
    def update_user_data(self, data):
        user = data['user']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        if len(data['new_password']) >= 8:
            new_hashed_password = bcrypt.hashpw(data['new_password'].encode(), bcrypt.gensalt()).decode()
            user.password = new_hashed_password
        user.save()
    
class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=45)
    last_activity = models.DateTimeField(default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    def friends(self):
        from social_app.models import Friendship
        friendships = Friendship.objects.filter(models.Q(friend_1=self) | models.Q(friend_2=self))
        friends = [friendship.friend_1 if friendship.friend_2 == self else friendship.friend_2 for friendship in friendships]
        return friends
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    def is_online(self):
        now = timezone.now()
        if self.last_activity > now - timedelta(minutes=5):
            return True
        return False