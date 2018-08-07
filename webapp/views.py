from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def webapp_main(request):
    context = dict()

    if request.user.is_authenticated:
        context['user'] = request.user

    return render(request, 'webapp/main.html', context)


def webapp_dashboard(request):
    context = dict()

    if request.user.is_authenticated:
        context['user'] = request.user
        return render(request, 'webapp/dashboard.html', context)
    else:
        return redirect('login')


@login_required
def webapp_view(request, pk):
    context = dict()

    if request.user.is_authenticated:
        context['user'] = request.user

    return render(request, 'webapp/dashboard_view.html')
