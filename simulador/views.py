from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'simulador/home.html')

@login_required
def inicio(request):
    return render(request, 'simulador/simulacao_inicio.html')



@login_required
def cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        empresa = request.POST.get('empresa')
        
        if nome:
            request.session['cliente'] = {
                'nome': nome,
                'empresa': empresa or ''
            }
            return redirect('simulador:elevador')
        else:
            messages.error(request, 'Por favor, informe o nome do cliente.')

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


@login_required
def cabine(request):
    if request.method == 'POST':
        dados = {
            'material': request.POST.get('material'),
            'espessura': request.POST.get('espessura'),
            'saida': request.POST.get('saida'),
            'piso': request.POST.get('piso'),
            'material_piso': request.POST.get('material_piso'),
            'largura_cabine': request.POST.get('largura_cabine'),
            'comprimento_cabine': request.POST.get('comprimento_cabine'),
            'altura_cabine': request.POST.get('altura_cabine'),
        }

        # Se material ou piso for "Outro", salva os campos adicionais
        if dados['material'] == 'Outro':
            dados['material_outro_nome'] = request.POST.get('material_outro_nome')
            dados['material_outro_valor'] = request.POST.get('material_outro_valor')

        if dados['piso'] == 'Por conta da empresa' and dados['material_piso'] == 'Outro':
            dados['material_piso_outro_nome'] = request.POST.get('material_piso_outro_nome')
            dados['material_piso_outro_valor'] = request.POST.get('material_piso_outro_valor')

        request.session['cabine'] = dados
        return redirect('simulador:resumo')

    return render(request, 'simulador/cabine.html')

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



