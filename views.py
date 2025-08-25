from django.shortcuts import render

from plugins.editorial_manager_transfer_service import forms


def manager(request):
    form = forms.DummyManagerForm()

    template = 'editorial_manager_transfer_service/manager.html'
    context = {
        'form': form,
    }

    return render(request, template, context)
