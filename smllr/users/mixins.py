from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class NonAnonymousUserRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure that the user is not anonymous.
    """
    
    def test_func(self):
        return self.request.user is not None and not self.request.user.is_anonymous

    def handle_no_permission(self):
        return redirect('shorturls_form')
