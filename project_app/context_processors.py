from .models import CreatorDetail, UserDetail


def session_account(request):
    email = request.session.get("session_key")
    role = request.session.get("role")
    account = None

    if email and role == "user":
        account = UserDetail.objects.filter(email=email).first()
    elif email and role == "creator":
        account = CreatorDetail.objects.filter(email=email, is_blocked=False).first()

    if not account:
        return {
            "site_account": None,
            "site_role": None,
            "site_is_logged_in": False,
        }

    return {
        "site_account": account,
        "site_role": role,
        "site_is_logged_in": True,
        "site_account_name": account.name,
    }
