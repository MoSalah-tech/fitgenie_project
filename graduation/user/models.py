from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin #user model
import datetime
import secrets



class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password,**extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
       
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
       

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password,**extra_fields)



class CustomUser(AbstractUser,PermissionsMixin):

    username=None
    name=models.CharField(max_length=255,blank=True, null=True)
    email=models.CharField(max_length=255,unique=True)
    password=models.CharField(max_length=255)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    is_verfied=models.BooleanField(default=False)
    

    objects=UserManager()
   
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[] 
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def __str__(self):
        return self.name or self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_username(self):
        return self.email
    



class Profile(models.Model):
    user=models.OneToOneField(CustomUser,related_name='profile', on_delete=models.CASCADE)
    name=models.CharField(max_length=40,null=True,blank=True)
    
    avatar=models.ImageField(upload_to=None,)
    bio=models.CharField(max_length=200,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at'] 

    def __str__(self):
        return self.user.get_full_name()



class GenAI(models.Model):
    user = models.ForeignKey(CustomUser,related_name='GenAI',on_delete=models.CASCADE)
    data = models.TextField() 
    def __str__(self):
        return self.user.email

class wGenAI(models.Model):
    user = models.ForeignKey(CustomUser,related_name='workGenAI',on_delete=models.CASCADE)
    data = models.TextField() 
    def __str__(self):
        return self.user.email

class userstate(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    fitness_goals_choices=(('Gain Weight','Gain Weight'),
                           ('Healthy Lifestyle','Healthy Lifestyle'),
                           ('Lose Weight','Lose Weight'),
                           )
    Work_Out_Level_choices=(('Intermediate','Intermediate'),
                           ('Beginner','Beginner'),
                           ('Advanced','Advanced'),
                           )
    user=models.OneToOneField(CustomUser,related_name='state', on_delete=models.CASCADE)
    height=models.IntegerField()
    weight=models.FloatField()
    age=models.IntegerField()
    bmi=models.FloatField()
    allergies=models.CharField(max_length=50)
    activity_level=models.FloatField()
    Work_Out_Level=models.CharField(max_length=50, choices=Work_Out_Level_choices)
    fitness_goals=models.CharField(max_length=50, choices=fitness_goals_choices)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.email
    


