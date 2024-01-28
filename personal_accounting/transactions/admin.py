import locale

from django.contrib import admin

from .forms import DocumentForm
from .models import Currency, Sink, Bank, Source, Loader, Document, Transaction

locale.setlocale(locale.LC_ALL, "de_CH.UTF-8")


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["currency"]


@admin.register(Sink)
class SinkAdmin(admin.ModelAdmin):
    list_display = ["name", "sink_type", "budget_fmt", "spending_fmt", "diff_fmt"]

    class Media:
        css = {
            "all": ("admin/css/sink.css",),
        }

    def spending(self, obj):
        return -1 * sum(t.amount for t in obj.transactions.all())

    def diff(self, obj):
        return obj.budget - self.spending(obj)

    def budget_fmt(self, obj):
        return locale.currency(obj.budget, grouping=True)

    def spending_fmt(self, obj):
        return locale.currency(self.spending(obj), grouping=True)

    def diff_fmt(self, obj):
        return locale.currency(self.diff(obj), grouping=True)

    diff_fmt.short_description = "diff"
    budget_fmt.short_description = "budget"
    spending_fmt.short_description = "spending"


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["bank", "account"]


@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):
    list_display = ["bank", "version"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["document", "item_no", "date", "amount", "currency", "info", "sink"]
    list_editable = ["sink"]
    list_filter = ["date", "document", "currency", "info", "sink"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["source", "year", "month"]
