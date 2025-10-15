from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string

def menu_hook(context):
    template = render_to_string(
        "editorial_manager_transfer_service/elements/menu_nav.html",
    )

    return template