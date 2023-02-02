from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .form import ResourceForm, DepartmentForm, MagStaffForm, EquipDescrForm, OwnsForm, CreateResource
from django.contrib.auth.decorators import login_required, permission_required
from .models import Resource, Department, MagStaff, Owns, EquipDescr
from .resources import DepartmentResource
from tablib import Dataset
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd

# Create your views here.

def base(request):
    
    context = {}
    return render(request, 'ITapp/index.html', context)

def home(request):
    
    context = {}
    return render(request, 'ITapp/home.html', context)

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('Home')

    page = 'login'

    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User Doesn't Exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')

        else:
            messages.error(request, "Username or Password doesn't exist")

    context = {'page':page}
    return render(request, 'ITapp/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('index')

def userProfile(request, pk):
    user = MagStaff.objects.get(email=pk)
    return redirect(request, 'ITapp/userProfile.html', {'user':user})

@login_required(login_url='login')
def simple_upload(request):
    data = None
    if request.method == 'POST':
        new_file = request.FILES['myfile']

        data = pd.read_excel(new_file.read())

        for i in data.index:
            resource = ResourceForm()
            resource = resource.save(commit=False)
            resource.id = data['id'][i]
            
            resource.equipType = data['equipType'][i]
            resource.addedDate = data['addedDate'][i]
            resource.save()

            owner = OwnsForm()
            owner = owner.save(commit=False)
            owner.ownRID = Resource.objects.get(id=data['id'][i])
            if not Department.objects.filter(deptName=data['Dept'][i]).exists():
                temp = DepartmentForm()
                temp = temp.save(commit=False)
                temp.deptName = data['Dept'][i]
                temp.save()
            owner.ownDept = Department.objects.get(deptName=data['Dept'][i])
            owner.save()

            descr = EquipDescrForm()
            descr = descr.save(commit=False)
            descr.equipID = Resource.objects.get(id=data['id'][i])
            descr.specificDescr = data['sDescr'][i]
            descr.genericDescr = data['gDescr'][i] 
            descr.save()


        messages.success(request, 'Uploaded')
        for idx in data.index:
            for column in data.columns:
                print(data[column][idx])


    return render(request,'ITapp/input.html', {'data':data})


def findResource(request):
    matches = []
    found = 0

    if request.method == 'POST':
    
        q = request.POST['q']
        p = request.POST['p']
        r = request.POST['r']

        if(q==None):
            q = ""

        if(p==None):
            p = ""

        if(r==None):
            r = ""

        resources = Resource.objects.filter(
            Q(equipType__icontains=q) |
            Q(addedDate__icontains=q)
        )

        dept = Owns.objects.filter(
            Q(ownDept__deptName__icontains=p) 
        )

        descr = EquipDescr.objects.filter(
            Q(specificDescr__icontains=r)|
            Q(genericDescr__icontains=r)
        )

        for resource in resources:
            for owned in dept:
                for des in descr:
                    if resource.id==owned.ownRID.id and resource.id==des.equipID.id:
                        matches.append(resource)

        found = len(matches)
        

    context = {'resources':matches, 'found':found}
    return render(request, 'ITapp/findResource.html', context)

@permission_required("ITapp.add_resource", raise_exception=True)
def createResource(request):
    form = CreateResource()
    
    if request.method == 'POST':
        form = CreateResource(request.POST)
        if form.is_valid():
            resource = ResourceForm()
            resource = resource.save(commit=False)
            resource.id = form.cleaned_data['resourceID']
            resource.equipType = form.cleaned_data['equipType']
            resource.addedDate = form.cleaned_data['addedDate']
            resource.save()

            owner = OwnsForm()
            owner = owner.save(commit=False)
            owner.ownRID = Resource.objects.get(id=form.cleaned_data['resourceID'])
            if not Department.objects.filter(deptName=form.cleaned_data['dept']).exists():
                temp = DepartmentForm()
                temp = temp.save(commit=False)
                temp.deptName = form.cleaned_data['dept']
                temp.save()
            owner.ownDept = Department.objects.get(deptName=form.cleaned_data['dept'])
            owner.save()

            descr = EquipDescrForm()
            descr = descr.save(commit=False)
            descr.equipID = Resource.objects.get(id=form.cleaned_data['resourceID'])
            descr.specificDescr = form.cleaned_data['sDescr']
            descr.genericDescr = form.cleaned_data['gDescr']
            descr.save()

            return redirect('resources')
        
    context = {'form':form}
    return render(request, 'ITapp/createResource.html', context)

@login_required(login_url='login')
def updateResource(request, pk):
    resource = Resource.objects.get(id=pk)
    form = ResourceForm(instance=resource)

    descr = EquipDescr.objects.get(equipID=resource)
    descrForm = EquipDescrForm(instance=descr)
    #auto fill initail values

    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        descrForm = EquipDescrForm(request.POST, instance=descr)

        #request.POST contains all info
        if form.is_valid():
            form.save()
            descrForm.save()
            return redirect('resources')

    context = {'form': form, 'descrForm':descrForm}
    return render(request, 'ITapp/updateResource.html', context)

def deleteResource(request, pk):
    resource = Resource.objects.get(id=pk)
    if request.method == 'POST':
        resource.delete()
        return redirect('resources')

    context = {'obj':resource}
    return render(request, 'ITapp/delete.html', context)

@permission_required("ITapp.add_resource", raise_exception=True)
def staff(request):
    
    form = MagStaffForm()
    staffs = MagStaff.objects.all()

    if request.method == 'POST':
        form = MagStaffForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            userName = form.cleaned_data['firstName']+" "+form.cleaned_data['lastName']
            userPass = form.cleaned_data['firstName']+"@rvce"
            userMail = form.cleaned_data['email']

            user = User.objects.create_user(userName, userMail, userPass)
            user.save()
            
            form.save()

    context = {'staffs':staffs, 'form':form}
    return render(request, 'ITapp/AuthStaff.html', context)

def filter(request, pk):
    resource = Resource.objects.get(id=pk)
    owner = Owns.objects.get(ownRID=pk)
    descr = EquipDescr.objects.get(equipID=pk)
    context = {'resource':resource, 'owner':owner, 'descr':descr}
    return render(request, 'ITapp/database.html', context)

