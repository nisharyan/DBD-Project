from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .form import ResourceForm, DepartmentForm, MagStaffForm, EquipDescrForm, OwnsForm, CreateResource, UserLoginForm
from django.contrib.auth.decorators import login_required, permission_required
from .models import Resource, Department, MagStaff, Owns, EquipDescr, SysAdmin
from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
import pandas as pd

# Create your views here.

def base(request):
    
    context = {}
    laptops = Resource.objects.filter(
        Q(equipType__icontains="Laptop") 
    )

    desktops = Resource.objects.filter(
        Q(equipType__icontains="Desktop") 
    )

    printers = Resource.objects.filter(
        Q(equipType__icontains="printer") 
    )

    routers = Resource.objects.filter(
        Q(equipType__icontains="router") 
    )

    servers = Resource.objects.filter(
        Q(equipType__icontains="server") 
    )


    context['laptops'] = len(laptops)
    context['servers'] = len(servers)
    context['routers'] = len(routers)
    context['desktops'] = len(desktops)
    context['printers'] = len(printers)
    return render(request, 'ITapp/Templates/ITapp/index.html', context)

def home(request):

    context = {}
    departments = Department.objects.all()

    laptops = Resource.objects.filter(
        Q(equipType__icontains="Laptop") 
    )

    desktops = Resource.objects.filter(
        Q(equipType__icontains="Desktop") 
    )

    printers = Resource.objects.filter(
        Q(equipType__icontains="printer") 
    )

    routers = Resource.objects.filter(
        Q(equipType__icontains="router") 
    )

    servers = Resource.objects.filter(
        Q(equipType__icontains="server") 
    )

    context['laptops'] = len(laptops)
    context['servers'] = len(servers)
    context['routers'] = len(routers)
    context['desktops'] = len(desktops)
    context['printers'] = len(printers)
    context['departments'] = departments 
    context['home'] = True

    return render(request, 'ITapp\index.html', context)

def loginPage(request):
    if request.user.is_authenticated:
            return redirect('Home')
    if request.method=="POST":
        form=UserLoginForm(request=request,data=request.POST)
        if form.is_valid():
            uname=form.cleaned_data['username']
            upass=form.cleaned_data['password']
            user=authenticate(username=uname,password=upass)
            if user is not None:
                login(request,user)
                return redirect('Home')        
    else:
        form=UserLoginForm()
    return render(request,'ITapp/login_register.html',{'form':form})

def logoutPage(request):
    logout(request)
    return redirect('index')

def userProfile(request, pk):
    user = MagStaff.objects.get(email=pk)
    print(user)
    return render(request, 'ITapp/userProfile.html', {'users':user})

class MyPasswordChangeView(PasswordChangeView):
    template_name = 'ITapp/changePassword.html'
    success_url = reverse_lazy('changePasswordDone')

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'ITapp/success.html'


@login_required(login_url='login')
def simple_upload(request):
    data = None
    if request.method == 'POST':
        new_file = request.FILES['myfile']

        data = pd.read_excel(new_file.read())

        for i in data.index:
            resource = ResourceForm()
            resource = resource.save(commit=False)
            data['id'][i] = int(data['id'][i])
            resource.id = int(data['id'][i])
            
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
        working = request.POST['working']

        if(q==None):
            q = ""

        if(p==None):
            p = ""

        if(r==None):
            r = ""
        if(working==None):
            working=""
        

        resources = Resource.objects.filter(
                Q(condition=False) |
                Q(id__icontains=q)|
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
        for res in resources:
            matches.append(res)
        found = len(matches)
        

    context = {'resources':matches, 'found':found}
    return render(request, 'ITapp/findResource.html', context)


def createResource(request):
    form = CreateResource()
    
    if request.method == 'POST':
        print('inside post')
        form = CreateResource(request.POST)
        if form.is_valid():
            
            resource = ResourceForm()
            resource = resource.save(commit=False)
            resource.id = form.cleaned_data['resourceID']
            print(resource.id)
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
            print("saved")

            descr = EquipDescrForm()
            descr = descr.save(commit=False)
            descr.equipID = Resource.objects.get(id=form.cleaned_data['resourceID'])
            descr.specificDescr = form.cleaned_data['sDescr']
            descr.genericDescr = form.cleaned_data['gDescr']
            descr.save()

            return redirect('/database/'+str(resource.id)+"/")
        
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

    if request.method == 'POST':

        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
    
        userName = firstname+" "+lastname
        userPass =  firstname+"@rvce"
        userMail =  email

        form = form.save(commit=False)
        
        form.auth_email = SysAdmin.objects.get(email=request.user.email)
        form.email= email
        form.firstName = firstname
        form.lastName =  lastname
        if not Department.objects.filter(deptName= request.POST.get("department")).exists():
                temp = DepartmentForm()
                temp = temp.save(commit=False)
                temp.deptName =  request.POST.get("department")
                temp.save()
        form.department = Department.objects.get(deptName= request.POST.get("department"))
        form.phoneNo = request.POST.get("phoneNo")

        form.save()
        user = User.objects.create_user(userName, userMail, userPass)
        user.save()
        messages.success(request, 'Staff Added')
        
        message = "testing the functionality"
        send_mail(
            'Staff added '+userName,
            message,
            settings.EMAIL_HOST_USER,
            [userMail],
            fail_silently=False,
        )

        return redirect('Home')

    context = {'form':form}
    return render(request, 'ITapp/AuthStaff.html', context)

def filter(request, pk):
    resource = Resource.objects.get(id=pk)
    owner = Owns.objects.get(ownRID=pk)
    descr = EquipDescr.objects.get(equipID=pk)
    context = {'resource':resource, 'owner':owner, 'descr':descr}
    return render(request, 'ITapp/database.html', context)

def resource_stats(request, pk):
    departments = Department.objects.all()

    objects = Resource.objects.filter(
        Q(equipType__icontains=pk) 
    )

    match = {}

    for i, dept in enumerate(departments):
        match[dept.deptName] = i

    count = [0]*len(departments)

    for obj in objects:
        resource = Owns.objects.get(ownRID=obj.id)
        count[match[resource.ownDept.deptName]] += 1



    context = {
        'count':count,
        'departments':departments,
    }

    return render(request, 'ITapp/resourceStats.html', context)

def department_stats(request, pk):
    dept = Department.objects.get(deptName=pk)
    temp = Resource.objects.filter(
        Q(equipType__icontains="Laptop") 
    )

    laptops = 0
    for item in temp:
        owns = Owns.objects.filter(ownRID=item.id)
        for own in owns:
            if(own.ownDept.deptName==pk):
                laptops+=1

    temp = Resource.objects.filter(
        Q(equipType__icontains="Server") 
    )

    servers = 0
    for item in temp:
        owns = Owns.objects.filter(ownRID=item.id)
        for own in owns:
            if(own.ownDept.deptName==pk):
                servers+=1

    temp = Resource.objects.filter(
        Q(equipType__icontains="Desktop") 
    )

    desktops = 0
    for item in temp:
        owns = Owns.objects.filter(ownRID=item.id)
        for own in owns:
            if(own.ownDept.deptName==pk):
                desktops+=1

    temp = Resource.objects.filter(
        Q(equipType__icontains="printer") 
    )

    printers = 0
    for item in temp:
        owns = Owns.objects.filter(ownRID=item.id)
        for own in owns:
            if(own.ownDept.deptName==pk):
                printers+=1

    temp = Resource.objects.filter(
        Q(equipType__icontains="router") 
    )

    routers = 0
    for item in temp:
        owns = Owns.objects.filter(ownRID=item.id)
        for own in owns:
            if(own.ownDept.deptName==pk):
                routers+=1

    context = {
        'laptops':laptops,
        'desktops':desktops,
        'printers':printers,
        'routers':routers,
        'servers':servers,
        'dept' : dept,
    }

    return render(request, 'ITapp/DepartmentResources.html', context)

def department(request):
    department = Department.objects.all()[1:]
    context = {'department':department}
    return render(request, 'ITapp/department.html', context)

def chats(request):
    context={}
    context = {}
    departments = Department.objects.all()

    for dept in departments:
        context[dept.deptName]=0
        context[dept.deptName+"_printers"]=0
        context[dept.deptName+"_servers"]=0
        context[dept.deptName+"_desktops"]=0
        context[dept.deptName+"_routers"]=0

    laptops = Resource.objects.filter(
        Q(equipType__icontains="Laptop") 
    )

    for laptop in laptops:
        temp = Owns.objects.get(ownRID=laptop.id)
        context[temp.ownDept.deptName]+=1

    desktops = Resource.objects.filter(
        Q(equipType__icontains="Desktop") 
    )

    for desktop in desktops:
        temp = Owns.objects.get(ownRID=desktop.id)
        context[temp.ownDept.deptName+"_desktops"]+=1

    printers = Resource.objects.filter(
        Q(equipType__icontains="printer") 
    )

    for printer in printers:
        temp = Owns.objects.get(ownRID=printer.id)
        context[temp.ownDept.deptName+"_printers"]+=1

    routers = Resource.objects.filter(
        Q(equipType__icontains="router") 
    )

    for router in routers:
        temp = Owns.objects.get(ownRID=router.id)
        context[temp.ownDept.deptName+"_routers"]+=1

    servers = Resource.objects.filter(
        Q(equipType__icontains="server") 
    )

    for server in servers:
        temp = Owns.objects.get(ownRID=server.id)
        context[temp.ownDept.deptName+"_servers"]+=1

    context['laptops'] = len(laptops)
    context['servers'] = len(servers)
    context['routers'] = len(routers)
    context['desktops'] = len(desktops)
    context['printers'] = len(printers)
    context['departments'] = departments 
    return render(request,'ITapp/chats.html',context)