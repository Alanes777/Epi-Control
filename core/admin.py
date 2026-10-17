from django.contrib import admin
from .models import Colaborador, EPI, Emprestimo, ItemEmprestimo


class ItemEmprestimoInline(admin.TabularInline):
    model = ItemEmprestimo
    extra = 1


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'setor', 'cargo', 'email', 'criado_em')
    search_fields = ('nome', 'matricula', 'setor', 'cargo')
    list_filter = ('setor', 'criado_em')
    ordering = ('nome',)


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = ('nome', 'certificado_aprovacao', 'quantidade_estoque', 'validade')
    search_fields = ('nome', 'certificado_aprovacao')
    list_filter = ('validade',)


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('id', 'colaborador', 'data_emprestimo', 'data_prevista_devolucao', 'status')
    list_filter = ('status', 'data_emprestimo')
    search_fields = ('colaborador__nome', 'colaborador__matricula')
    inlines = [ItemEmprestimoInline]
