from django.contrib import admin

from .forms import DocumentForm
from .models import Currency, Sink, Bank, Source, Loader, Document, Transaction

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['currency']

@admin.register(Sink)
class SinkAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['bank', 'account']

@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):
    list_display = ['bank', 'version']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['document', 'item_no', 'date', 'amount', 'currency', 'info', 'sink']
    list_editable = ['sink']
    list_filter = ['date', 'document', 'currency', 'info', 'sink']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['loader', 'source', 'year', 'month']