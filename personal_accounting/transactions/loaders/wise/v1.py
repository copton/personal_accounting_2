import csv
from datetime import datetime
import json
import hashlib


date_fmt = "%d-%m-%Y"

from transactions.models import Transaction, Document, Currency

def load(doc: Document):
    with open(doc.file.path, "r") as fd:
        reader = csv.DictReader(fd)
        for n, point in enumerate(reader):
            amount = float(point["Amount"])
            if amount == 0.0:
                continue

            checksum = hashlib.md5(json.dumps(point, sort_keys=True).encode('utf-8')).hexdigest()
            date = datetime.strptime(point["Date"], date_fmt)
            currency = Currency.objects.get(currency=point["Currency"])
            info = point["Merchant"] if point["Merchant"] else point["Description"]
            tx = Transaction.objects.create(
                source_checksum=checksum,
                document=doc,
                item_no=n,
                date=date.date(),
                amount=amount,
                currency=currency,
                info=info,
            )
            tx.save()
