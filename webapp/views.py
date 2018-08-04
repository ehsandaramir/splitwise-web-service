from django.shortcuts import render, redirect


def webapp_main(request):
    context = {}
    return render(request, 'webapp/main.html', context)


def webapp_dashboard(request):
    context = {
        'user': request.user,
    }

    if request.user.is_authenticated:
        return render(request, 'webapp/dashboard.html', context)
    else:
        return redirect('login')
