from django.shortcuts import render


def legal_mentions(request):
    return render(request, "core/credits.html")
