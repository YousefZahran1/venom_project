from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import Poll, Choice, Vote
from .forms import PollAddForm, EditPollForm, ChoiceAddForm
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# --- Chat View (using Hugging Face API) ---
@login_required
@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("message", "")

            if not question:
                return JsonResponse({"error": "Please provide a question."}, status=400)

            # Hugging Face API URL for gpt2 model
            url = "https://api-inference.huggingface.co/models/gpt2"
            headers = {
                "Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": question}

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                return JsonResponse({"error": response_data.get("error", "Unknown error")}, status=500)

            # Extract generated response
            answer = response_data[0].get("generated_text", "No response received.")
            return JsonResponse({"reply": answer})

        except Exception as e:
            return JsonResponse({"error": f"Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@login_required
def chat_page(request):
    return render(request, "polls/chat.html")

# --- Rest of the views ---
@login_required
def polls_list(request):
    all_polls = Poll.objects.all()
    search_term = ""

    if "name" in request.GET:
        all_polls = all_polls.order_by("text")
    if "date" in request.GET:
        all_polls = all_polls.order_by("pub_date")
    if "vote" in request.GET:
        all_polls = all_polls.annotate(Count("vote")).order_by("vote__count")
    if "search" in request.GET:
        search_term = request.GET["search"]
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 6)  # Show 6 polls per page
    page = request.GET.get("page")
    polls = paginator.get_page(page)

    context = {
        "polls": polls,
        "search_term": search_term,
    }
    return render(request, "polls/polls_list.html", context)

# --- Dashboard View ---
@login_required
def dashboard(request):
    polls = Poll.objects.all()
    poll_data = [
        {
            "question": poll.text,
            "unique_voters": Vote.objects.filter(poll=poll).values("user").distinct().count(),
            "pub_date": poll.pub_date
        }
        for poll in polls
    ]
    return render(request, "polls/dashboard.html", {"poll_data": poll_data})


# --- List Polls by User ---
@login_required
def list_by_user(request):
    user_polls = Poll.objects.filter(owner=request.user)
    paginator = Paginator(user_polls, 7)
    page = request.GET.get("page")
    polls = paginator.get_page(page)
    return render(request, "polls/polls_list.html", {"polls": polls})

# --- Add Poll ---
@login_required
def polls_add(request):
    if request.user.has_perm("polls.add_poll"):
        if request.method == "POST":
            form = PollAddForm(request.POST)
            if form.is_valid():
                poll = form.save(commit=False)
                poll.owner = request.user
                poll.save()
                Choice(poll=poll, choice_text=form.cleaned_data["choice1"]).save()
                Choice(poll=poll, choice_text=form.cleaned_data["choice2"]).save()
                messages.success(request, "Poll added successfully!", extra_tags="alert alert-success")
                return redirect("polls:list")
        else:
            form = PollAddForm()
        return render(request, "polls/add_poll.html", {"form": form})
    else:
        return HttpResponse("You don't have permission to add a poll.")

# --- Edit Poll ---
@login_required
def polls_edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect("polls:list")

    if request.method == "POST":
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            messages.success(request, "Poll updated successfully!", extra_tags="alert alert-success")
            return redirect("polls:list")
    else:
        form = EditPollForm(instance=poll)
    return render(request, "polls/poll_edit.html", {"form": form, "poll": poll})

# --- Delete Poll ---
@login_required
def polls_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect("polls:list")
    poll.delete()
    messages.success(request, "Poll deleted successfully!", extra_tags="alert alert-success")
    return redirect("polls:list")

# --- Add Choice ---
@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect("polls:list")

    if request.method == "POST":
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.poll = poll
            choice.save()
            messages.success(request, "Choice added successfully!", extra_tags="alert alert-success")
            return redirect("polls:edit", poll.id)
    else:
        form = ChoiceAddForm()
    return render(request, "polls/add_choice.html", {"form": form})

# --- Delete Choice ---
@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    if request.user != choice.poll.owner:
        return redirect("polls:list")
    choice.delete()
    messages.success(request, "Choice deleted successfully!", extra_tags="alert alert-success")
    return redirect("polls:edit", choice.poll.id)

# --- Poll Detail and Voting ---
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if not poll.active:
        return render(request, "polls/poll_result.html", {"poll": poll})
    return render(request, "polls/poll_detail.html", {"poll": poll})

@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get("choice")
    if not poll.user_can_vote(request.user):
        messages.error(request, "You have already voted!", extra_tags="alert alert-warning")
        return redirect("polls:detail", poll_id)

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        Vote.objects.create(user=request.user, poll=poll, choice=choice)
        return render(request, "polls/poll_result.html", {"poll": poll})
    else:
        messages.error(request, "No choice selected!", extra_tags="alert alert-warning")
        return redirect("polls:detail", poll_id)

# --- End Poll ---
@login_required
def end_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect("polls:list")
    poll.active = False
    poll.save()
    return render(request, "polls/poll_result.html", {"poll": poll})

@login_required
def choice_edit(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect("home")

    if request.method == "POST":
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Choice updated successfully.",
                extra_tags="alert alert-success alert-dismissible fade show",
            )
            return redirect("polls:edit", poll.id)
    else:
        form = ChoiceAddForm(instance=choice)

    context = {
        "form": form,
        "edit_choice": True,
        "choice": choice,
    }
    return render(request, "polls/add_choice.html", context)
