from django.db.models import F
from django.http import HttpResponseRedirect
from .models import Question, Choice
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def logged_in_view(request):
    if not request.user.is_authenticated:
        return redirect("/polls/login-view/")

    return render(request, "polls/logged_in_page.html")    

def register_view(request, context={}):
    template_name = "registration/register_view.html"
    return render(request, template_name, context)

def register(request):
    username = request.POST["username"]
    password = request.POST["email"]
    password = request.POST["password"]
    
    errors = {}
    
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        errors['error'] = True
        print(' ------------- 1')
        # raise ValidationError('Username or email already taken.')
        response = register_view(request, errors)
        return response
        # return render(request, 'registration/register_view.html', {'errors': errors})

    print(' ------- 2')
    # user = User.objects.create_user(username, email, password)
    # user.save()
    # login(request, user)
    # return redirect('/polls/logged-in/')
    
def login_view(request):
    template_name = "registration/login_view.html"
    return render(request, template_name)

def login_user(request):
    print("running login_user(request) ")
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        return redirect('/polls/logged-in/')
    
    return redirect('/polls/login-view')

def my_view(request):
    if not request.user.is_authenticated:
        """ 
        non-logged-in and non-registered guests:
        - can view public models and data
        - can upload and train models
        """        
        if "condition " == "data.is_private":
            return redirect(f"{settings.LOGIN_URL}?next={request.path}") 
    if request.user.is_authenticated:        
        "can also view and manage personal private models and data"

def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

@login_required(login_url='/polls/login')
def view_user_private_models(request):
    pass

def logout_view(request):
    logout(request)
    return redirect("/polls/")

def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
    ]

def process_model_options_view(request):
    template_name = "polls/process_model_options.html"
    return render(request, template_name)

def human_reinforced_feedback_view(request):
    template_name = "polls/human_reinforced_feedback.html"
    return render(request, template_name)

def final_task_analytics_view(request):
    template_name = "polls/final_task_analytics.html"
    return render(request, template_name)

def previous_tasks_view(request):
    template_name = "polls/previous_tasks.html"
    return render(request, template_name)

def personal_model_repo_view(request):
    template_name = "polls/personal_model_repo.html"
    return render(request, template_name)

def personal_dataset_repo_view(request):
    template_name = "polls/personal_dataset_repo.html"
    return render(request, template_name)

def personal_dataset_analysis_view(request):
    template_name = "polls/personal_dataset_analysis.html"
    return render(request, template_name)