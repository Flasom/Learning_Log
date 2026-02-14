from django.shortcuts import render
from .models import Topic, Entry
from .forms import Topic_Form, Entry_Form
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def index(request):
    """Página principal do Learning_Log"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """Mostra todos os assuntos"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Mostra um único assunto com todas as suas entradas."""
    topic = Topic.objects.get(id=topic_id)

    # Garante que o assunto pertence ao usuário atual
    if topic.owner != request.user:
        raise Http404
    
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Adiciona um novo assunto."""
    if request.method != 'POST':
        # Nenhum dado submetido; cria um formulário em branco
        form = Topic_Form()
    else:
        # Dados de POST submetidos; processa os dados
        form = Topic_Form(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('topics'))
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Adiciona uma nova anotação a um assunto."""
    topic = Topic.objects.get(id=topic_id)

    # Garante que o assunto pertence ao usuário atual
    if topic.owner != request.user:
        raise Http404
    
    if request.method != 'POST':
        # Nenhum dado submetido; cria um formulário em branco
        form = Entry_Form()
    else:
        # Dados de POST submetidos; processa os dados
        # Pega apenas os dados passado no POST, não o considerando o formulário completo
        form = Entry_Form(data=request.POST)
        if form.is_valid():
            # Cria um objeto do formulario, mas não o commita para que possa continuar sendo editado
            new_entry = form.save(commit=False)
            new_entry.topic = topic  # acessa o valor topic do BD e o iguala ao id coerente
            new_entry.save()  # Salva definitivamente o formulario no BD
            return HttpResponseRedirect(reverse('topic', args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edita um anotação existente."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    # Garante que o assunto pertence ao usuário atual
    if topic.owner != request.user:
        raise Http404
    
    if request.method != 'POST':
        # Requisição inicial; preenche previamente o formulário com a entrada atual
        form = Entry_Form(instance=entry)
    else:
        # Dados de Post submetidos; processa os dados
        form = Entry_Form(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('topic', args=[topic.id]))
        
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)