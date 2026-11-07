from django.shortcuts import redirect, resolve_url
from django.conf import settings


class AuthRequiredMiddleware:
    """
    Middleware de controle de acesso do sistema EPI Control.
    Garante que todas as rotas do sistema sejam protegidas por padrão,
    exigindo que o usuário esteja autenticado.

    Rotas isentas de autenticação prévia:
    1. /login/ (tela de login)
    2. /logout/ (ação de logout)
    3. /admin/ (painel administrativo do Django - possui seu próprio controle de acesso)
    4. Arquivos estáticos e de mídia (/static/ e /media/)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Rotas isentas que não exigem login prévio
        is_exempt = (
            path.startswith('/login') or
            path.startswith('/logout') or
            path.startswith('/admin') or
            (bool(settings.STATIC_URL) and path.startswith(settings.STATIC_URL)) or
            (bool(getattr(settings, 'MEDIA_URL', None)) and path.startswith(settings.MEDIA_URL))
        )

        if not request.user.is_authenticated and not is_exempt:
            login_url = resolve_url(settings.LOGIN_URL)
            return redirect(f"{login_url}?next={path}")

        return self.get_response(request)
