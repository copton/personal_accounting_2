# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import json
from xml.dom import minidom

from transactions.models import Transaction, Document, Currency

date_fmt = "%Y-%m-%d"


def data_of(element):
    """get the data of an element"""
    if element is None:
        return None
    return element.firstChild.data


def all_data_off(element):
    """recursively get all data of an element and its children"""
    res = []

    def go_rec(node):
        if node.nodeType == node.TEXT_NODE:
            res.append(node.data)
            return

        for c in node.childNodes:
            go_rec(c)

    go_rec(element)
    return res


def element(path, parent):
    """retrieve the element identified by the path relative to the parent"""
    if len(path) == 0:
        return parent

    p = path.pop(0)
    try:
        child = parent.getElementsByTagName(p)[0]
    except IndexError:
        return None

    return element(path, child)


def entry(node):
    """turn a CAMT node into an element of the import dataset"""
    d = {}
    d["id"] = data_of(element(["AcctSvcrRef"], node))
    d["type"] = data_of(element(["CdtDbtInd"], node))

    d["date"] = data_of(element(["BookgDt", "Dt"], node))

    amt = element(["Amt"], node)
    d["currency"] = amt.getAttribute("Ccy")
    d["amount"] = data_of(amt)

    d["creditor_IBAN"] = data_of(
        element(["NtryDtls", "TxDtls", "RltdPties", "CdtrAcct", "Id", "IBAN"], node)
    )

    d["creditor_otherid"] = data_of(
        element(
            ["NtryDtls", "TxDtls", "RltdPties", "CdtrAcct", "Id", "Othr", "Id"], node
        )
    )

    d["creditor_name"] = data_of(
        element(["NtryDtls", "TxDtls", "RltdPties", "Cdtr", "Nm"], node)
    )

    d["debitor_name"] = data_of(
        element(["NtryDtls", "TxDtls", "RltdPties", "Dbtr", "Nm"], node)
    )

    info = element(["NtryDtls", "TxDtls", "RmtInf"], node)
    if info is None:
        d["info"] = None
    else:
        d["info"] = ";".join(all_data_off(info))

    d["additional_info"] = data_of(element(["AddtlNtryInf"], node))

    return d


infos = {
    "creditor_IBAN",
    "creditor_otherid",
    "creditor_name",
    "debitor_name",
    "info",
    "additional_info",
}


def load(doc: Document):
    """load the dataset of a CAMT file"""
    with open(doc.file.path, "r") as fd:
        xmldoc = minidom.parse(fd)
        entries = [entry(n) for n in xmldoc.getElementsByTagName("Ntry")]

        for n, point in enumerate(entries):
            print(point)
            amount = float(point["amount"])
            if point["type"] == "DBIT":
                amount *= -1
            checksum = hashlib.md5(
                json.dumps(point, sort_keys=True).encode("utf-8")
            ).hexdigest()
            date = datetime.strptime(point["date"], date_fmt)
            currency = Currency.objects.get(currency=point["currency"])
            info = json.dumps({k: v for k, v in point.items() if k in infos})

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
