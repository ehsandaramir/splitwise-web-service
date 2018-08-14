from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def webapp_main(request):
    context = dict()

    if request.user.is_authenticated:
        context['user'] = request.user

    return render(request, 'webapp/main.html', context)


@login_required
def webapp_dashboard(request):
    context = dict()
    context['user'] = None

    if request.user.is_authenticated:
        context['user'] = request.user
        return render(request, 'webapp/dashboard.html', context)
    else:
        return redirect('login')


@login_required
def webapp_edit(request, pk):
    context = dict()

    if request.user.is_authenticated:
        context['user'] = request.user

    return render(request, 'webapp/dashboard_view.html')


def webapp_signup(request):
    context = dict()
    context['user'] = request.user
    return render(request, 'registration/signup.html', context)
