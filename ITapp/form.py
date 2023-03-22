from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Resource, MagStaff, Owns, SysAdmin, EquipDescr, Department

class PasswordChangingForm(PasswordChangeForm):
	old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))
	new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))
	new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))

	class Meta:
		model = User
		fields = ('old_password', 'new_password1', 'new_password2')

class ResourceForm(ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'

class SysAdminForm(ModelForm):
    class Meta:
        model = SysAdmin
        fields = '__all__'

class MagStaffForm(ModelForm):
    class Meta:
        model = MagStaff
        fields = '__all__'
        exclude = ('auth_email', )

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

class OwnsForm(ModelForm):
    class Meta:
        model = Owns
        fields = '__all__'

class EquipDescrForm(ModelForm):
    class Meta:
        model = EquipDescr
        fields = '__all__'

        exclude = ['equipID']

class CreateResource(forms.Form):
    resourceID = forms.CharField(max_length = 20)
    equipType = forms.CharField(max_length = 30)
    addedDate = forms.DateField()
    gDescr = forms.CharField(max_length = 200)
    sDescr = forms.CharField(max_length = 200)
    dept = forms.CharField(max_length = 20)

    class Meta:
        fields = '__all__'
    
class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.PasswordInput()