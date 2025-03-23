from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils.calculations import calcular_dimensionamento_completo, calcular_componentes

from .models import Usuario, Custo, Parametro
from .forms import UsuarioForm, CustoForm, ParametroForm

# Funções auxiliares para verificação de permissões
def is_admin(user):
    return user.nivel == 'admin'

def is_engenharia(user):
    return user.nivel in ['admin', 'engenharia']

# PAGINAS

def home(request):
    context = {
        'use_content_box': True,
        'user_level': request.user.nivel if request.user.is_authenticated else None
    }
    return render(request, 'simulador/home.html', context)

@login_required
def inicio(request):
    return render(request, 'simulador/simulacao_inicio.html')

@login_required
def cliente(request):
    if request.method == 'POST':
        nome_cliente = request.POST.get('nome_cliente')
        nome_empresa = request.POST.get('nome_empresa')
        
        if nome_cliente:
            request.session['cliente'] = {
                'nome': nome_cliente,
                'empresa': nome_empresa or ''
            }
            return redirect('simulador:elevador')
        else:
            messages.error(request, 'Por favor, identifique o cliente.')
    
    return render(request, 'simulador/cliente.html')

@login_required
def elevador(request):
    if request.method == 'POST':
        # Aqui você pode armazenar os dados no session
        request.session['elevador_data'] = request.POST  # ou fazer um tratamento adequado
        return redirect('simulador:portas')  # <- Certifique-se de que está indo para a próxima etapa
    return render(request, 'simulador/elevador.html')

@login_required
def portas(request):
    if request.method == 'POST':
        # Aqui você pode salvar os dados da sessão ou do banco se quiser
        # request.session['portas_data'] = request.POST

        return redirect('simulador:cabine')  # 🔁 redireciona para a view da cabine

    return render(request, 'simulador/portas.html')

def cabine(request):
    if "respostas" not in request.session:
        request.session["respostas"] = {}

    if request.method == 'POST':
        # Capturar dados do formulário
        material = request.POST.get('material')
        espessura = request.POST.get('espessura')
        saida = request.POST.get('saida')
        piso = request.POST.get('piso')
        altura_cabine = float(request.POST.get('altura_cabine'))

        # Salvar dados na sessão
        request.session["respostas"]["Material"] = material
        if material != "Outro":
            request.session["respostas"]["Espessura"] = espessura
        else:
            request.session["respostas"]["Material Outro Nome"] = request.POST.get('outro_nome')
            request.session["respostas"]["Material Outro Valor"] = request.POST.get('outro_valor')
        request.session["respostas"]["Saída"] = saida
        request.session["respostas"]["Altura da Cabine"] = altura_cabine
        request.session["respostas"]["Piso"] = piso

        if piso == "Por conta da empresa":
            request.session["respostas"]["Material Piso Cabine"] = request.POST.get('material_piso')
            if request.POST.get('material_piso') == "Outro":
                request.session["respostas"]["Material Piso Outro Nome"] = request.POST.get('outro_nome_piso')
                request.session["respostas"]["Material Piso Outro Valor"] = request.POST.get('outro_valor_piso')

        # Calcular dimensionamento
        dimensionamento, explicacoes = calcular_dimensionamento_completo(request.session["respostas"])
        
        # Salvar informações calculadas na sessão
        request.session["respostas"]["Largura da Cabine"] = dimensionamento['cab']['largura']
        request.session["respostas"]["Comprimento da Cabine"] = dimensionamento['cab']['compr']

        # Calcular componentes
        componentes, custos, custo_total, todos_custos = calcular_componentes(dimensionamento, request.session["respostas"])

        # Salvar componentes e custos na sessão
        request.session["componentes"] = componentes
        request.session["custos"] = custos
        request.session["custo_total"] = custo_total

        return redirect('simulador:proxima_pagina')

    # Se for GET, renderizar o formulário
    respostas = request.session.get("respostas", {})
    contrapeso = respostas.get("Contrapeso", "Lateral")
    modelo_elevador = respostas.get("Modelo do Elevador", "")
    
    # Calcular dimensionamento para pré-preencher os campos
    dimensionamento, _ = calcular_dimensionamento_completo(respostas)
    
    context = {
        'respostas': respostas,
        'contrapeso': contrapeso,
        'opcoes_saida': ["Padrão", "Oposta"] if contrapeso != "Traseiro" else ["Padrão"],
        'altura_inicial': 2.30 if modelo_elevador == "Passageiro" else 2.10,
        'largura_cabine': dimensionamento['cab']['largura'],
        'comprimento_cabine': dimensionamento['cab']['compr'],
    }

    return render(request, 'simulador/cabine.html', context)

@login_required
def resumo(request):
    respostas = {
        "cliente": request.session.get("cliente"),
        "elevador": request.session.get("elevador_data"),
        "portas": request.session.get("portas_data"),
        "cabine": request.session.get("cabine"),
    }
    return render(request, 'simulador/resumo.html', {'respostas': respostas})

@login_required
def reiniciar_simulacao(request):
    if request.method == 'POST':
        # Evita apagar a sessão de login
        keys_to_clear = ['cliente', 'elevador_data', 'portas_data', 'cabine']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]
        return redirect('simulador:cliente')
    
    return redirect('simulador:resumo')  # fallback para GET

# AUTENTICACAO

def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('simulador:home')

# CRUDS

# Views para USUARIOS 
@login_required
@user_passes_test(is_admin)
def usuario_list(request):
    # Ordena por username para garantir consistência na paginação
    usuarios_list = Usuario.objects.filter(is_active=True).order_by('username')
    
    # Configurar paginação (10 itens por página)
    paginator = Paginator(usuarios_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página
        usuarios = paginator.page(1)

    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página
        usuarios = paginator.page(paginator.num_pages)
    
    return render(request, 'simulador/usuario_list.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin)
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso.')
            # Limpa todas as mensagens após adicionar para evitar duplicação
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('simulador:usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'simulador/usuario_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso.')
            # Limpa todas as mensagens após adicionar para evitar duplicação
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('simulador:usuario_list')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'simulador/usuario_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        try:
            # Em vez de excluir, apenas desative o usuário
            usuario.is_active = False
            usuario.save()
            messages.success(request, 'Usuário desativado com sucesso.')
            # Limpa todas as mensagens após adicionar para evitar duplicação
            storage = messages.get_messages(request)
            storage.used = True
        except Exception as e:
            messages.error(request, f'Erro ao desativar usuário: {str(e)}')
        return redirect('simulador:usuario_list')
    return render(request, 'simulador/usuario_confirm_delete.html', {'usuario': usuario})

# Views para Custos 
@login_required
@user_passes_test(is_engenharia)
def custo_list(request):
    custos_list = Custo.objects.all().order_by('codigo')
    
    # Configurar paginação (10 itens por página)
    paginator = Paginator(custos_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        custos = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página
        custos = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página
        custos = paginator.page(paginator.num_pages)
    
    return render(request, 'simulador/custo_list.html', {'custos': custos})

@login_required
@user_passes_test(is_engenharia)
def custo_create(request):
    if request.method == 'POST':
        form = CustoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Custo criado com sucesso.')
            # Limpa todas as mensagens após adicionar para evitar duplicação
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('simulador:custo_list')
    else:
        form = CustoForm()
    return render(request, 'simulador/custo_form.html', {'form': form})

@login_required
@user_passes_test(is_engenharia)
def custo_update(request, pk):
    custo = get_object_or_404(Custo, pk=pk)
    if request.method == 'POST':
        # Criamos um dicionário com os dados do POST para usar no formulário
        post_data = {
            'codigo': request.POST.get('codigo'),
            'descricao': request.POST.get('descricao'),
            'unidade': request.POST.get('unidade'),
            'valor': request.POST.get('valor')
        }
        
        # Usamos o dicionário para criar o formulário
        form = CustoForm(post_data, instance=custo)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Custo atualizado com sucesso.')
            return redirect('simulador:custo_list')
        else:
            # Se o formulário não for válido, continuamos na página com os erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = CustoForm(instance=custo)
    
    return render(request, 'simulador/custo_form.html', {'form': form})

@login_required
@user_passes_test(is_engenharia)
def custo_delete(request, pk):
    custo = get_object_or_404(Custo, pk=pk)
    if request.method == 'POST':
        custo.delete()
        messages.success(request, 'Custo excluído com sucesso.')
        # Limpa todas as mensagens após adicionar para evitar duplicação
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('simulador:custo_list')
    return render(request, 'simulador/custo_confirm_delete.html', {'custo': custo})

# Views para Parâmetros (versão modificada)
@login_required
@user_passes_test(is_admin)
def parametro_list(request):
    # Buscar todos os parâmetros, ordenados por nome do parâmetro
    parametros_list = Parametro.objects.all().order_by('parametro')
    
    # Configurar paginação (10 itens por página)
    paginator = Paginator(parametros_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        parametros = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página
        parametros = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página
        parametros = paginator.page(paginator.num_pages)
    
    return render(request, 'simulador/parametro_list.html', {'parametros': parametros})

@login_required
@user_passes_test(is_admin)
def parametro_create(request):
    if request.method == 'POST':
        form = ParametroForm(request.POST)
        if form.is_valid():
            parametro = form.save()
            messages.success(request, 'Parâmetro criado com sucesso.')
            # Redireciona diretamente para a lista, não para o detalhe
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('simulador:parametro_list')
    else:
        form = ParametroForm()
    return render(request, 'simulador/parametro_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def parametro_update(request, pk):
    parametro = get_object_or_404(Parametro, pk=pk)
    if request.method == 'POST':
        form = ParametroForm(request.POST, instance=parametro)
        if form.is_valid():
            parametro = form.save()
            messages.success(request, 'Parâmetro atualizado com sucesso.')
            # Redireciona diretamente para a lista, não para o detalhe
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('simulador:parametro_list')
    else:
        form = ParametroForm(instance=parametro)
    return render(request, 'simulador/parametro_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def parametro_delete(request, pk):
    parametro = get_object_or_404(Parametro, pk=pk)
    if request.method == 'POST':
        parametro.delete()
        messages.success(request, 'Parâmetro excluído com sucesso.')
        # Limpa todas as mensagens após adicionar para evitar duplicação
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('simulador:parametro_list')
    return render(request, 'simulador/parametro_confirm_delete.html', {'parametro': parametro})