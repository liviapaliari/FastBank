import decimal

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import *
from .serializer import *
from .models import aleatorios


# FUNÇÃO QUE RETORNA O ID DO USUÁRIO LOGADO, ATRAVÉS DO TOKEN JWT
def get_id(request):
    token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[1]
    dados = AccessToken(token)
    return dados["user_id"]


# API PRODUTOS
class ProdutosViewSet(viewsets.ModelViewSet):
    # PERMITE QUE QUEM NÃO ESTEJA AUTENTICADO APENAS VEJA OS DADOS
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Produtos.objects.all()
    serializer_class = ProdutosSerializer


# API CLIENTES - ROTA PROTEGIDA
class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # RETORNA OS DADOS DO CLIENTE QUE ESTÁ LOGADO
    def list(self, request, *args, **kwargs):
        id_user = get_id(request)
        usuario = CustomUser.objects.get(pk = id_user)
        return Response(CustomUserSerializer(usuario).data)
    

# API TRANSAÇÕES - ROTA PROTEGIDA
class TransacoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Transacoes.objects.all()
    serializer_class = TransacoesSerializer

    def create(self, request, *args, **kwargs):
        # FILTRANDO O USUÁRIO DESTINATÁRIO PELA CHAVE CPF
        destinatario = CustomUser.objects.get(cpf = request.data["chave"])
        id_remetente = get_id(request)
        conta_remetente = Contas.objects.get(fk_cliente = id_remetente)
        
        # SE O DESTINATÁRIO EXISTIR E SE ELE NÃO FOR IGUAL AO REMETENTE
        if destinatario is not None and destinatario.id != id_remetente:
            # SE O SALDO DO REMETENTE É MAIOR OU IGUAL AO VALOR TRANSFERIDO
            if conta_remetente.saldo >= decimal.Decimal(request.data["valor"]):
                conta_remetente.saldo -= decimal.Decimal(request.data["valor"])
                conta_remetente.save()

                conta_destinatario = Contas.objects.get(fk_cliente = destinatario.id)
                # SE O DESTINATÁRIO EXISTIR
                if conta_destinatario is not None:
                    conta_destinatario.saldo += decimal.Decimal(request.data["valor"])
                    conta_destinatario.save()
            else:
                # SE NÃO, RETORNA UM ERRO PARA O FRONT-END
                    raise serializers.ValidationError({"Saldo Insuficiente"})
            request.data["fk_remetente"] = id_remetente
            request.data["fk_destinatario"] = destinatario.id
            request.data["nome_destinatario"] = destinatario.nome_razao
            request.data["tipo"] = "Transferência"
        else:
            # SE NÃO, RETORNA UM ERRO PARA O FRONT-END
            raise serializers.ValidationError({"Conta Destinatária não encontrada"})
        return super().create(request, *args, **kwargs)
    
    # RETORNA AS TRANSAÇÕES DE QUEM ESTÁ LOGADO
    def list(self, request, *args, **kwargs):
        id_user = get_id(request)
        transacoes = Transacoes.objects.filter(fk_remetente = id_user)
        return Response(TransacoesSerializer(transacoes, many=True).data)


# API CARTÕES - ROTA PROTEGIDA
class CartoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cartoes.objects.all()
    serializer_class = CartoesSerializer

    def create(self, request, *args, **kwargs):
        request.data["fk_cliente"] = get_id(request)
        request.data["numero"] = aleatorios(16)
        request.data["cvv"] = aleatorios(3)
        request.data["validade"] = "2024-01-01"
        return super().create(request, *args, **kwargs)


# API ENDEREÇOS - ROTA PROTEGIDA
class EnderecosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Enderecos.objects.all()
    serializer_class = EnderecosSerializer

    def create(self, request, *args, **kwargs):
        request.data["fk_cliente"] = get_id(request)
        return super().create(request, *args, **kwargs)


# API CONTAS - ROTA PROTEGIDA
class ContasViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Contas.objects.all()
    serializer_class = ContasSerializer

    # RETORNA A CONTA BANCÁRIA DO USUÁRIO QUE ESTÁ LOGADO
    def list(self, request, *args, **kwargs):
        id = get_id(request)
        conta = Contas.objects.get(fk_cliente = id)
        return Response(ContasSerializer(conta).data)
    

    # QUERY PARAMETER PARA SELECIONAR OS DADOS DE ACORDO COM O ID USER
    # def get_queryset(self):
    #     queryset = Contas.objects.all()
    #     id = self.request.query_params.get("id")

    #     # SE PASSOU QUERY PARAMETER
    #     if id is not None:
    #         queryset = queryset.filter(fk_cliente = id)
    #         return queryset
        
    #     return super().get_queryset()


class EmprestimosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Emprestimos.objects.all()
    serializer_class = EmprestimosSerializer

    def create(self, request, *args, **kwargs):
        # VALOR TOTAL COM JUROS (VALOR + (VALOR * TAXA * Nº PARCELAS))
        # VALOR DAS PARCELAS (VALOR TOTAL COM JUROS / Nº PARCELAS)

        valor = float(request.data["valor"])
        taxa_juros = 0.38
        qtd_parcela = int(request.data["qtd_parcela"])

        valor_total = valor + (valor * taxa_juros * qtd_parcela)
        request.data["valor_parcela"] = valor_total / qtd_parcela
        request.data["fk_cliente"] = get_id(request)
        request.data["valor_juros"] = valor_total

        conta = Contas.objects.get(fk_cliente = get_id(request))
        conta.saldo += decimal.Decimal(request.data["valor"])
        conta.save()

        return super().create(request, *args, **kwargs)