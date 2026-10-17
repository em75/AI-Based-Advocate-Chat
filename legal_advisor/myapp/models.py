from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class Login(AbstractUser):
    userType = models.CharField(max_length=100)
    viewPass = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.username


class UserRegistration(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True)
    dob = models.DateField()
    gender = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to="profile")
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)
    Account_no=models.IntegerField(null=True,blank=True)
    pin_no=models.IntegerField(null=True,blank=True)
    district= models.CharField(max_length=100, null=True)
    aadhaar= models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
    
class Advocate(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True)
    dob = models.DateField()
    gender = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to="profile")
    files = models.FileField(null=True, upload_to="profile")
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)
    district= models.CharField(max_length=100, null=True)
    category=models.CharField(max_length=100, null=True)
    qualification=models.CharField(max_length=100, null=True)
    Regfee=models.CharField(max_length=100, null=True,default="Pending")
    advo_rating=models.IntegerField(null=True,blank=True)
    code = models.CharField(max_length=100, null=True)


    def __str__(self):
        return self.name
    
class Case_Category(models.Model):
    Category=models.CharField(max_length=100, null=True)
    Description=models.CharField(max_length=100, null=True)

class BNS_sections(models.Model):
    BNS=models.CharField(max_length=100, null=True)
    Description=models.CharField(max_length=100, null=True)

class Feedback(models.Model):
    uid=models.ForeignKey(UserRegistration, on_delete=models.CASCADE, null=True)
    aid=models.ForeignKey(Advocate, on_delete=models.CASCADE, null=True)
    sub = models.CharField(max_length=100, null=True)
    Feedback=models.CharField(max_length=100, null=True)
    Type=models.CharField(max_length=100, null=True)
    date=models.CharField(max_length=100, null=True)
    

class Case_request(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE, null=True)
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, null=True)
    sub = models.CharField(max_length=100, null=True)
    desc=models.CharField(max_length=100, null=True)
    date=models.CharField(max_length=100, null=True)
    request=models.CharField(max_length=100, null=True, default="pending")
    status=models.CharField(max_length=100, null=True, default="Not_Updated")


class Case_details(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE, null=True)
    rid = models.ForeignKey(Case_request, on_delete=models.CASCADE, null=True)
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, null=True)
    file = models.FileField(null=True)
    desc=models.CharField(max_length=100, null=True)
    fees=models.CharField(max_length=100, null=True)
    status=models.CharField(max_length=100, null=True, default='Not_Paid')

class Chat(models.Model):
    uid = models.ForeignKey(UserRegistration, on_delete=models.CASCADE,)
    Advo = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    message = models.CharField(max_length=300, blank=True, default='')
    file = models.FileField(null=True, blank=True, upload_to="chat_files")
    date = models.DateField(auto_now=True)
    time = models.CharField(max_length=100)
    utype = models.CharField(max_length=100)
    
class Rating(models.Model):
    rating=models.IntegerField(null=True, blank=True)
    aid=models.ForeignKey(Advocate, on_delete=models.CASCADE,null=True)
    uid=models.ForeignKey(UserRegistration, on_delete=models.CASCADE,null=True)
    date=models.DateField(null=True, blank=True,auto_now_add=True)
    rid=models.ForeignKey(Case_request, on_delete=models.CASCADE,null=True)

class CaseNote(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    content = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('advocate', 'user')

    def __str__(self):
        return f"Note by {self.advocate.name} for {self.user.name}"

class OTPModel(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    