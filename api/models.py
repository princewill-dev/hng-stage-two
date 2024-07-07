import random
import string
import uuid
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import AbstractUser

def generate_userid():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def generate_org_id():
    length = 10
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class User(AbstractUser):
    userId = models.CharField(
        max_length=10, 
        unique=True, 
        default=generate_userid,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]{10}$',
                message='userId must be a 10-character alphanumeric string.',
                code='invalid_userid'
            )
        ]
    )
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstName', 'lastName']

    def save(self, *args, **kwargs):
        if not self.username:
            # Generate a unique username
            self.username = str(uuid.uuid4())
        super(User, self).save(*args, **kwargs)
        
        # Create an organization for the user
        organisation, created = Organisation.objects.get_or_create(
            created_by=self,
            defaults={
                'name': f"{self.firstName}'s Organisation",
                'description': f"This organisation belongs to {self.firstName}"
            }
        )
        if created:
            # Clear any existing members and add only the current user
            organisation.members.clear()
            organisation.members.add(self)

class Organisation(models.Model):
    orgId = models.CharField(max_length=10, default=generate_org_id, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='created_organisations', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='member_organisations')

    def save(self, *args, **kwargs):
        if not self.orgId:
            self.orgId = generate_org_id()
        if not self.description:
            self.description = f"This organisation belongs to {self.created_by.firstName}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
