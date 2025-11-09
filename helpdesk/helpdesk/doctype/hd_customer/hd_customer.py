# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe import _
from frappe.model.document import Document


class HDCustomer(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": _("Name"),
                "key": "name",
                "width": "17rem",
                "type": "Data",
            },
            {
                "label": _("Domain"),
                "key": "domain",
                "width": "24rem",
                "type": "Data",
            },
            {
                "label": _("Created On"),
                "key": "creation",
                "width": "8rem",
                "type": "Datetime",
            },
        ]
        return {"columns": columns}
