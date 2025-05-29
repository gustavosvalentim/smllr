from allauth.socialaccount.models import SocialAccount


def user_social_account(request):
    context = {
        'socialaccount': {}
    }

    if not request.user or request.user.pk is None:
        return context
    
    socialaccount = SocialAccount.objects.filter(user=request.user).first()
    if not socialaccount:
        return context
    
    return {
        'socialaccount': {
            'picture': socialaccount.extra_data.get('picture')
        }
    }
