from django.contrib.auth.forms import UserCreationForm

UserCreationForm.declared_fields["password1"].required = False
UserCreationForm.declared_fields["password2"].required = False
