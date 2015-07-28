# -*- encoding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from apps.Departamentos.models import Departamento
from apps.Usuarios.models import Usuario, Rol

def login(request):
    if request.method == 'POST':
        #Tomar los valores mandados al hacer log in
        usuario = request.POST.get('username','')
        password = request.POST.get('pass','')
        
        #Autentificar que el usuario exista
        user = auth.authenticate(username=usuario, password=password)

        #Si el usuario existe  y está activo, se inicia la sesión
        if user is not None and user.is_active:
            auth.login(request, user)

            #Se asigna una variable de sesión para poder acceder a ella desde cualquier página
            request.session['usuario'] = usuario
            request.session['rol'] = user.usuario.rol.id
            
            if request.session['rol'] == 1:
                return redirect('/inicio-secretaria/')
            elif request.session['rol'] == 2:
                return redirect('/inicio-jefedep/')
            else:
                return redirect('/inicio-administrador/')
        else:
            return render(request,'login.html', {'errors': "Usuario o contraseña incorrectos"})
    else:
        return render(request,'login.html')

def logout(request):
    try:
        auth.logout(request)
    except KeyError:
        pass
    return redirect('/')
    
#Verificar si el usuario está logeado, en caso contrario, redirecciona a página de log in
@login_required(login_url='/')
def inicio_admin(request):
    #revisa que el usuario tenga permisos necesarios para ver el contenido de esta página
    departamentos = Departamento.objects.all()
    if request.session['rol'] == 3:
        banner = True
        return render(request, 'inicio-administrador.html', locals())
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def form_sistema_modificar_jefedep(request):
    errors = 'No hay jefes de departamento disponibles, crear uno antes de seguir con la modificación de jefe de departamento'
    if request.session['rol'] == 3:
        if request.method == 'POST':
            post_nombreDepartamento = request.POST.get('departamento', '')
            departamento = Departamento.objects.get(nombre=post_nombreDepartamento)
            try:
                jefeActual = departamento.jefeDep
                opcionesJefeDepartamento = Usuario.objects.filter(user__is_active=True, rol__id__gte=1, departamento=None)
            except ObjectDoesNotExist:
                return render(request, 'modificar-jefe-departamento.html', locals())
            return render(request, 'modificar-jefe-departamento.html', locals())
        else:
            return redirect('/inicio-administrador/')
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def sistema_modificar_jefedep(request):
    if request.session['rol'] == 3:
        if request.method == 'POST':
            #Tomar valores del POST
            post_jefeActual = request.POST.get('jefeActual', '')
            post_departamento = request.POST.get('departamento', '')
            post_nuevoJefe = request.POST.get('nuevoJefe', '')

            #¿Qué hacer con el antiguo jefe de departamento?

            #Query del objeto del nuevo jefe
            nuevoJefe = Usuario.objects.get(user__username = post_nuevoJefe)

            #Query del departamento del jefe actual
            departamento = Departamento.objects.get(nombre = post_departamento)

            #Sustitución del jefe actual por el nuevo
            departamento.jefeDep = nuevoJefe

            #Guardar los cambios en la base de datos
            departamento.save()

        return redirect('/inicio-administrador/')
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def nuevo_departamento(request):
    if request.session['rol'] == 3:
        #Revisar si se entra a la página por POST
        if request.method == 'POST':
            #Obtener los campos del nuevo departamento
            post_codigo = request.POST.get('id','')
            post_nombre = request.POST.get('nombre', '')
            post_nuevoJefe = request.POST.get('nuevoJefe', '')
            
            #Hacer query del nuvo jefe
            nuevoJefe = Usuario.objects.get(user__username=post_nuevoJefe)

            #Crear el nuevo departamento
            nuevoDepartamento = Departamento(id=post_codigo, nombre=post_nombre, jefeDep=nuevoJefe)
            
            #Guardar en la base de datos el nuevo departamento
            nuevoDepartamento.save()

            return redirect('/inicio-administrador/')
        #Si no se entra con POST, se regresa el formulario de nuevo departamento
        else:
            errors = 'No hay jefes de departamento disponibles, crear uno antes de seguir con la creación de departamento'
            opcionesJefeDepartamento = Usuario.objects.filter(rol = 2).filter(departamento = None)
            return render(request, 'nuevo_departamento.html', locals())
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def nuevo_jefe(request):
    if request.session['rol'] == 3:
        if request.method == 'POST':
            usuario = request.POST.get('username','')
            password = request.POST.get('password', '')
            codigo = request.POST.get('codigo','')
            nombre = request.POST.get('nombre','')
            apellido = request.POST.get('apellido','')
            if User.objects.filter(username = usuario ).exists():
                errors = 'Ya existe registro con ese nombre'
                return render(request,'nuevo_jefeDep.html',locals())
            else:
                Jefe_rol = Rol.objects.get(id = 2 )
                usuario_user = User.objects.create_user(username=usuario, first_name=nombre, 
                                                        last_name=apellido, password = password)
                Jefe_usuario = Usuario(user=usuario_user, codigo=codigo, rol=Jefe_rol)
                usuario_user.save()
                Jefe_usuario.save()
                return redirect('/inicio-administrador/')
        else:
            return render(request, 'nuevo_jefeDep.html')
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def nueva_secretaria(request):
    if request.session['rol'] == 3 or request.session['rol'] == 2:
        if request.method == 'POST':
            usuario = request.POST.get('username','')
            password = request.POST.get('password', '')
            codigo = request.POST.get('codigo','')
            nombre = request.POST.get('nombre','')
            apellido = request.POST.get('apellido','')
            if User.objects.filter(username = usuario ).exists():
                errors = 'Ya existe registro con ese nombre'
                return render(request,'nueva-secretaria.html',locals())
            else:
                Jefe_rol = Rol.objects.get(id = 1 )
                usuario_user = User.objects.create_user(username=usuario, first_name=nombre, 
                                                        last_name=apellido, password = password)
                Jefe_usuario = Usuario(user=usuario_user, codigo=codigo, rol=Jefe_rol)
                usuario_user.save()
                Jefe_usuario.save()
                if request.session['rol'] == 3:
                    return redirect('/inicio-administrador/')
                elif request.session['rol'] == 2:
                    return redirect('/inicio-jefedep/')
        else:
            return render(request, 'nueva-secretaria.html')
    else:
        return render(request, 'PermisoDenegado.html')

@login_required(login_url='/')
def activar_usuarios(request):
    if request.session['rol'] == 3:
        usuarios = User.objects.all();
        return render(request, 'activar_usuarios.html', locals())
