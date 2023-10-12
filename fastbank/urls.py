from .import views
from rest_framework.routers import DefaultRouter


rota = DefaultRouter()

# REGISTROS NA ROTA
rota.register("contas", viewset=views.ContasViewSet)
rota.register("cartoes", viewset=views.CartoesViewSet)
rota.register("produtos", viewset=views.ProdutosViewSet)
rota.register("clientes", viewset=views.CustomUserViewSet)
rota.register("enderecos", viewset=views.EnderecosViewSet)
rota.register("transacoes", viewset=views.TransacoesViewSet)
rota.register("emprestimos", viewset=views.EmprestimosViewSet)

urlpatterns = [] + rota.urls