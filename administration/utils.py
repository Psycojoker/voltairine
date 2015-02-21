from django.contrib.auth.decorators import user_passes_test


def is_staff(view):
    return user_passes_test(lambda user: user.is_staff)(view)
