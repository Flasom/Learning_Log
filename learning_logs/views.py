from django.shortcuts import render
from .models import Topic, Entry, History
from .forms import Topic_Form, Entry_Form, History_Form
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


def index(request):
    """Página principal do Learning_Log"""
    
    context = {'history': return_history(request)}
    return render(request, 'learning_logs/index.html', context)

@login_required
def return_history(request):
    history = History.objects.filter(owner=request.user).all().order_by('-date_added')[:10]
    return history

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
@csrf_protect
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
            history_new_topic(request, new_topic.text)
            return HttpResponseRedirect(reverse('topics'))
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
@csrf_protect
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
            history_new_entry(request, new_entry.text, topic)
            return HttpResponseRedirect(reverse('topic', args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
@csrf_protect
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
            history_edit_entry(request, entry.text, topic)
            return HttpResponseRedirect(reverse('topic', args=[topic.id]))
        
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
@csrf_protect
def edit_topic(request,  topic_id):
    """Edita um tópico existente"""
    topic = Topic.objects.get(id=topic_id)

    # Garante que o tópico pertence ao usuário atual
    if topic.owner != request.user:
        raise Http404
    
    if request.method != 'POST':
        # Requisição inicial; preenche previamente o formulário com a entrada atual
        form = Topic_Form(instance=topic)
    else:
        # Dados de Post submetidos; processa os dados
        form = Topic_Form(instance=topic, data=request.POST)
        if form.is_valid():
            form.save()
            history_edit_topic(request, topic.text)
            return HttpResponseRedirect(reverse('topics'))     
    
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    """Deleta um tópico."""
    topic = Topic.objects.get(id=topic_id)

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Excluiu o tópico ' + topic.text + "."
    new_history.owner = request.user
    new_history.save()
    
    topic.delete()

    return HttpResponseRedirect(reverse('topics'))

@login_required
def delete_entry(request, entry_id):
    """Deleta uma anotação."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Excluiu a anotação ' + entry.text + " do Tópico " + topic.text + "."
    new_history.owner = request.user
    new_history.save()

    entry.delete()

    return HttpResponseRedirect(reverse('topic', args=[topic.id]))

@login_required
def delete_confirm_entry(request, entry_id):
    """Verifica se o usúario realmente quer excluir uma anotação."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    context = {'entry': entry, 'topic': topic}
    return render(request, 'learning_logs/confirm_entry.html', context)

@login_required
def delete_confirm_topic(request, topic_id):
    """Verifica se o usúario realmente quer excluir um Tópico."""
    topic = Topic.objects.get(id=topic_id)
    context = {'topic': topic}
    return render(request, 'learning_logs/confirm_topic.html', context)


def history_new_entry(request, entry_name, topic_id):
    """Adiciona a ação ao histórico."""
    topic = topic_id

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Criou a anotação ' + entry_name + " no Tópico " + topic.text + "."
    new_history.owner = request.user
    new_history.save()

def history_edit_entry(request, entry_name, topic_id):
    """Adiciona a ação ao histórico."""
    topic = topic_id

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Editou a anotação ' + entry_name + " do Tópico " + topic.text + "."
    new_history.owner = request.user
    new_history.save()

def history_new_topic(request, topic_name):
    """Adiciona a ação ao histórico."""

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Criou o tópico ' + topic_name + "."
    new_history.owner = request.user
    new_history.save()

def history_edit_topic(request, topic_name):
    """Adiciona a ação ao histórico."""

    new = History_Form()
    new_history = new.save(commit=False)
    new_history.title = 'Editou o tópico ' + topic_name + "."
    new_history.owner = request.user
    new_history.save()

@login_required
def history(request):
    """Renderiza a pagina de histórico."""
    history = History.objects.filter(owner=request.user).all().order_by('-date_added')
    context = {'history': history}
    return render(request, 'learning_logs/history.html', context)