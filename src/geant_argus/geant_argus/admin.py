from django.contrib.admin import ModelAdmin, site
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sessions.models import Session

# Mark password fields non-required so that we can create users without password
# that can login through SSO
UserCreationForm.declared_fields["password1"].required = False
UserCreationForm.declared_fields["password2"].required = False


User = get_user_model()


class SessionAdmin(ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.all_users = {}

    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "user", "_session_data", "expire_date"]
    readonly_fields = ["_session_data"]

    def user(self, obj):
        user_id = int(obj.get_decoded().get("_auth_user_id"))
        return self.all_users.get(user_id)

    def get_queryset(self, request):
        self.all_users = {u.id: u for u in User.objects.all()}
        return super().get_queryset(request)


site.register(Session, SessionAdmin)
