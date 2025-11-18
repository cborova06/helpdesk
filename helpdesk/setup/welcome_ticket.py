import frappe
from frappe.desk.form.assign_to import add as add_assign

AUTHOR_EMAIl = "info@brvsoftware.com.tr"
AUTHOR_NAME = "BRVSoftware"
CONTENT = """
<p>
Merhaba 👋
<br><br>
HelpdeskAI'ı denemeye karar verdiğiniz için teşekkür ederiz. Ekiplerin müşterileriyle
daha iyi iletişim kurup kaliteli destek verebilmesi için bu uygulamayı geliştirdik.
<br><br>
Başlamanın en kolay yolu bir destek e-posta adresi tanımlamak ve ilk talepleri bu adrese
iletmektir. Böylece Helpdesk içinde tüm akışı uçtan uca görmüş olursunuz.
<br><br>
Herhangi bir sorunla karşılaşırsanız lütfen web sitemiz üzerinden bizimle iletişime geçin:
<a href="https://brvsoftware.com.tr" target="_blank">https://brvsoftware.com.tr</a>
<br><br>
Sevgiler,
<br>
BRVSoftware
</p>
"""


def create_welcome_ticket():
    create_contact()
    create_ticket()


def create_ticket():
    if frappe.db.count("HD Ticket"):
        return

    d = frappe.new_doc("HD Ticket")
    d.subject = "HelpdeskAI'a Hoş Geldiniz"
    d.description = CONTENT
    d.raised_by = AUTHOR_EMAIl
    d.contact = AUTHOR_NAME
    d.via_customer_portal = True
    d.insert()
    add_assign(
        {
            "doctype": "HD Ticket",
            "name": d.name,
            "assign_to": ["Administrator"],
        }
    )


def create_contact():
    frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": AUTHOR_NAME,
            "email_ids": [{"email_id": AUTHOR_EMAIl, "is_primary": 1}],
        }
    ).insert()
