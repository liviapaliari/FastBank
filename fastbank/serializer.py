from rest_framework import serializers
from .models import *


# SERIALIZER PRODUTOS
class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = ["id", "nome", "descricao", "preco", "disponibilidade"]


# SERIALIZER CLIENTES
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "cpf", "nome_razao", "email", "telefone", "dt_nasc_abertura", "rg", "foto"]


# SERIALIZER TRANSAÇÕES
class TransacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacoes
        fields = ["id", "fk_remetente", "fk_destinatario", "nome_destinatario", "tipo", "descricao", "valor", "data_hora"]


# SERIALIZER CARTÕES
class CartoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartoes
        fields = ["id", "fk_cliente", "numero", "cvv", "validade"]


# SERIALIZER ENDEREÇOS
class EnderecosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enderecos
        fields = ["id", "fk_cliente", "logradouro", "numero", "bairro", "complemento", "cidade", "uf", "cep"]


# SERIALIZER CONTAS
class ContasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contas
        fields = ["id", "fk_cliente", "agencia", "numero", "saldo", "tipo", "ativa"]


# SERIALIZER EMPRÉSTIMOS
class EmprestimosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimos
        fields = ["id", "fk_cliente", "valor", "qtd_parcela", "valor_parcela", "valor_juros"]