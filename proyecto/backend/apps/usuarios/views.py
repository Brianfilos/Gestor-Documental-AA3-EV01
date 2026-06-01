from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Rol
from .forms import LoginForm, UsuarioForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    from apps.documentos.models import Documento
    total_docs = Documento.objects.count()
    total_usuarios = Usuario.objects.count()
    docs_activos = Documento.objects.filter(estado='activo').count()
    docs_recientes = Documento.objects.order_by('-fechaCarga')[:5]
    context = {
        'total_docs': total_docs,
        'total_usuarios': total_usuarios,
        'docs_activos': docs_activos,
        'docs_recientes': docs_recientes,
    }
    return render(request, 'usuarios/dashboard.html', context)


@login_required
def usuario_list(request):
    usuarios = Usuario.objects.select_related('idRol').all()
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            else:
                usuario.set_unusable_password()
            usuario.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/formulario.html', {'form': form, 'accion': 'Crear'})


@login_required
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuario_list')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/formulario.html', {'form': form, 'accion': 'Editar', 'objeto': usuario})


@login_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('usuario_list')
    return render(request, 'usuarios/confirmar_eliminar.html', {'objeto': usuario, 'tipo': 'usuario'})
