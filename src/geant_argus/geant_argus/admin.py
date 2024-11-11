from django.contrib.auth.forms import UserCreationForm

# Mark password fields non-required so that we can create users without password
# that can login through SSO
UserCreationForm.declared_fields["password1"].required = False
UserCreationForm.declared_fields["password2"].required = False
