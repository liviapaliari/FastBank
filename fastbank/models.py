from random import randint
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


# FUNÇÃO GERAR NÚMEROS ALEATÓRIOS
def aleatorios(numero):
    variavel = ""
    for i in range(numero):
        variavel += str(randint(0, 9))
    return variavel


# TABELA PRODUTOS
class Produtos(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    disponibilidade = models.BooleanField(default=True)


# MANAGER CUSTOM USER
class CustomUserManager(BaseUserManager):
    # CRIAR USUÁRIO NORMAL
    def create_user(self, cpf, password, **extra_fields):
        # FAZER AJUSTES NO RAISE VALUE ERROR
        if not cpf:
            raise ValueError(_("O campo CPF é obrigatório"))
        
        user = self.model(cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save()

        # GERAR NÚMERO DE CONTA ALEATÓRIO
        numero_conta = aleatorios(8)
        
        # CRIANDO CONTA NO BANCO
        Contas.objects.create(fk_cliente=user, agencia="1234", numero=numero_conta, saldo=500, tipo="Conta-Corrente", ativa=True)

        return user

    # CRIAR SUPER USER
    def create_superuser(self, cpf, password, **extra_fields):
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(cpf, password, **extra_fields)


# TABELA CUSTOM USER
class CustomUser(AbstractBaseUser):
    cpf = models.CharField(max_length=11, unique=True)
    nome_razao = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=11)
    dt_nasc_abertura = models.DateField()
    rg = models.CharField(max_length=9, unique=True)
    foto = models.ImageField(upload_to="media", blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "cpf"
    REQUIRED_FIELDS = ["nome_razao", "email", "telefone", "dt_nasc_abertura", "rg"]

    objects = CustomUserManager()

    def __str__(self):
        return self.cpf
    

# TABELA TRANSAÇÕES
class Transacoes(models.Model):
    fk_remetente = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="fk_remetente")
    fk_destinatario = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="fk_destinatario")
    nome_destinatario = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    chave = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100, null=True, blank=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data_hora = models.DateTimeField(auto_now=True)


# TABELA CARTÃO
class Cartoes(models.Model):
    fk_cliente = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    numero = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    validade = models.DateField()

    # MOSTRAR O NÚMERO DO CARTÃO EM VEZ DO ID
    def __str__(self) -> str:
        return self.numero


# TABELA CONTA
class Contas(models.Model):
    fk_cliente = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    agencia = models.CharField(max_length=4)
    numero = models.CharField(max_length=12)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=20)
    ativa = models.BooleanField(default=True)


# TABELA ENDEREÇOS
class Enderecos(models.Model):
    fk_cliente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    complemento = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=8)


# TABELA EMPRÉSTIMOS
class Emprestimos(models.Model):
    fk_cliente = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    qtd_parcela = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=8, decimal_places=2)
    valor_juros = models.DecimalField(max_digits=8, decimal_places=2)