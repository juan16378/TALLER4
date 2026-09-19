"""
Vistas de captura de camara.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def capture_view(request):
    """
    Pagina principal: muestra el feed de la camara (getUserMedia) para
    poder capturar una foto del rostro del usuario autenticado.
    """
    return render(request, "capture/capture.html")
