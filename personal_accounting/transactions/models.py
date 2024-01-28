import importlib

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


def document_upload_path(instance, filename):
    # Construct the file path: uploads/documents/year/month/filename
    return f"static/uploads/documents/{instance.year}/{instance.month}/{filename}"


class Currency(models.Model):
    currency = models.CharField(max_length=3)

    def __str__(self):
        return self.currency


class Sink(models.Model):
    SINK_TYPES = [
        ("expense", "expense"),
        ("shadow", "shadow"),
    ]
    name = models.CharField(max_length=255)
    budget = models.IntegerField(default=0)
    sink_type = models.CharField(max_length=20, choices=SINK_TYPES)

    def __str__(self):
        return self.name


class Bank(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Source(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    account = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.bank} {self.account}"


class Loader(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    technical_name = models.CharField(max_length=30)
    version = models.PositiveSmallIntegerField(default=1)
    doc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bank} v. {self.version}"


class Document(models.Model):
    source = models.ForeignKey(Source, on_delete=models.PROTECT)
    loader = models.ForeignKey(Loader, on_delete=models.PROTECT)
    file = models.FileField(upload_to=document_upload_path)
    year = models.PositiveIntegerField(default=2024)
    month = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="Value must be greater than or equal to 1."),
            MaxValueValidator(12, message="Value must be less than or equal to 12."),
        ]
    )

    def delete(self, *args, **kwargs):
        # Delete the file when the Document object is deleted
        storage, path = self.file.storage, self.file.path
        super().delete(*args, **kwargs)
        storage.delete(path)

    def __str__(self):
        return f"{self.source} {self.year}-{self.month}"

    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)

        # Run custom code to process the uploaded file
        self.process_file()

    def process_file(self):
        name = (
            f"transactions.loaders.{self.loader.technical_name}.v{self.loader.version}"
        )
        module = importlib.import_module(name)
        module.load(self)


class Transaction(models.Model):
    source_checksum = models.CharField(max_length=32, unique=True)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="transactions"
    )
    item_no = models.IntegerField()
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    info = models.TextField()
    sink = models.ForeignKey(
        Sink,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    doc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.amount}{self.currency} - {self.document.source}"
