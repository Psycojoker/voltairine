from django.contrib.auth.decorators import user_passes_test


def user_can_see_administration_interface(view):
    return user_passes_test(lambda user: user.is_staff or user.group_is_admin_set.exists())(view)


def user_is_staff(view):
    return user_passes_test(lambda user: user.is_staff)(view)
