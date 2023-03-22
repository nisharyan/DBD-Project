from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Resource(models.Model):
    equipType = models.CharField(max_length=50, null=True)
    addedDate = models.DateField(auto_now_add=False, default=None)
    condition = models.BooleanField(default=True)
    class Meta:
        ordering = [ '-addedDate' ]
    def __str__(self):
        return self.equipType+" "+str(self.id)

class Department(models.Model):
    deptName = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.deptName

class Owns(models.Model):
    ownDept = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    ownRID = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, to_field='id')

    def __str__(self):
        return str(self.ownRID.id)

    class Meta:
        unique_together = (('ownDept', 'ownRID'))

class EquipDescr(models.Model):
    equipID = models.ForeignKey(Resource, on_delete=models.CASCADE, unique=True, primary_key=True )
    specificDescr = models.TextField(null=True, blank=True)
    genericDescr = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.equipID.id)

class SysAdmin(models.Model):
    email = models.EmailField(max_length=254, primary_key=True)
    phoneNo = models.CharField(max_length=10, blank=True)
    firstName = models.CharField(max_length=25)
    lastName = models.CharField(max_length=25)

    def __str__(self):
        return self.firstName+" "+self.lastName

class MagStaff(models.Model):
    email = models.EmailField(max_length=254, primary_key=True)
    auth_email = models.ForeignKey(SysAdmin, null=True, on_delete=models.SET_NULL, to_field='email', blank=True)
    firstName = models.CharField(max_length=25)
    lastName = models.CharField(max_length=25)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    phoneNo = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.firstName+" "+self.lastName



   


