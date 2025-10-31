import frappe
from frappe import _
from frappe.utils import now_datetime, add_days
from random import randint, choice


def seed_dashboard_data(count: int = 10):
    """Seed some demo HD Tickets so Dashboard charts show data.
    - Half open, half resolved
    - Assign to current user
    - Spread across last 10 days
    """
    user = frappe.session.user

    # pick a resolved status and an open status (fallback to the first ones)
    open_status = (
        frappe.get_all("HD Ticket Status", filters={"category": "Open"}, pluck="name")
        or ["Open"]
    )[0]
    resolved_status = (
        frappe.get_all(
            "HD Ticket Status", filters={"category": "Resolved"}, pluck="name"
        )
        or ["Resolved"]
    )[0]

    made = []
    for i in range(count):
        day_offset = randint(0, 9)
        created_on = add_days(now_datetime(), -day_offset)
        doc = frappe.get_doc(
            {
                "doctype": "HD Ticket",
                "subject": f"Seed Ticket #{i+1}",
                "description": "Seeded for dashboard demo",
            }
        )
        doc.insert(ignore_permissions=True)

        # assign to current user
        frappe.db.set_value("HD Ticket", doc.name, "_assign", frappe.as_json([user]))

        # randomly open/resolved
        is_resolved = i % 2 == 0
        status = resolved_status if is_resolved else open_status
        updates = {"status": status}

        if is_resolved:
            # mark as resolved with basic timings
            updates.update(
                {
                    "agreement_status": "Fulfilled",
                    "first_responded_on": add_days(created_on, 0),
                    "first_response_time": 2 * 3600,  # 2 hours
                    "resolution_date": add_days(created_on, 1),
                    "resolution_time": 24 * 3600,  # 1 day
                    "feedback_rating": choice([3, 4, 5]),
                }
            )

        frappe.db.set_value("HD Ticket", doc.name, updates)
        # move creation into the past to spread charts
        frappe.db.sql(
            "update `tabHD Ticket` set creation=%s where name=%s",
            (created_on, doc.name),
        )

        made.append(doc.name)

    frappe.db.commit()
    print({"created": made})


def list_kb_articles():
    """List all published Knowledge Base articles with content preview."""
    articles = frappe.get_all(
        "HD Article",
        fields=["name", "title", "category", "status"],
        filters={"status": "Published"},
        limit=100,
    )
    
    # Get content preview for each article
    for article in articles:
        doc = frappe.get_doc("HD Article", article.name)
        article["content_preview"] = (doc.content or "")[:500]
    
    print(frappe.as_json(articles, indent=2))
    return articles


def seed_kb_tickets(count=10):
    """
    Generate realistic HD Tickets based on Knowledge Base articles.
    Creates tickets with multi-turn Communication threads.
    """
    import random
    from frappe.utils import add_days, now_datetime
    
    # Use hardcoded users: borovacihan@gmail.com as customer, Administrator as agent
    customer_email = "borovacihan@gmail.com"
    agent_email = "admin@example.com"  # Administrator
    
    # Ticket scenarios based on actual KB articles
    scenarios = [
        {
            "subject": _("Modem kurulumu sırasında bağlantı problemi"),
            "description": "Yeni aldığım ADSL modemimi kurmaya çalışıyorum ancak internet bağlantısı sağlayamıyorum. Modemi prize taktım, DSL ışığı yanıyor ama internet erişimi yok. Ne yapmam gerekiyor?",
            "category": "c3rcp5si0d",
            "priority": "Medium",
            "communications": [
                {
                    "content": "Merhaba,<br><br>ADSL modem kurulum konusunda yardımcı olabilirim. Modem ışıklarının durumunu kontrol edelim:<br><br>1. Power/PWR ışığı sürekli yanıyor mu?<br>2. DSL ışığı sürekli yanıyor mu yoksa yanıp sönüyor mu?<br>3. Internet/WAN ışığı yanıyor mu?<br><br>Ayrıca telefonunuzdan çevir sesi geliyor mu?<br><br>Bilgileri paylaşırsanız size daha detaylı yardımcı olabilirim.<br><br>Saygılarımla,<br>Destek Ekibi",
                    "from_customer": False,
                },
                {
                    "content": "Teşekkürler. DSL ışığı sürekli yanıyor, PWR ışığı da yanıyor ama Internet ışığı hiç yanmıyor. Telefon çevir sesi normal geliyor.",
                    "from_customer": True,
                },
                {
                    "content": "Anladım. Internet ışığının yanmaması modem konfigürasyonu ile ilgili olabilir. Size aşağıdaki adımları öneriyorum:<br><br>1. Modemin arkasındaki reset tuşuna 10 saniye basılı tutarak fabrika ayarlarına dönün<br>2. Modemi 192.168.1.1 adresinden yönetim paneline girin<br>3. Kullanıcı adı: admin, Şifre: admin (genelde böyledir)<br>4. Internet bağlantı ayarlarından PPPoE seçeneğini işaretleyin<br>5. Kullanıcı adınızı ve şifrenizi girin<br><br>Detaylı modem kurulum rehberimiz için <a href='/kb/csdais6v6t'>Modem Nasıl Kurulur</a> makalesine göz atabilirsiniz.<br><br>İyi günler.",
                    "from_customer": False,
                },
                {
                    "content": "Harika! Anlattığınız şekilde yaptım ve internet çalışmaya başladı. Çok teşekkür ederim!",
                    "from_customer": True,
                },
            ],
            "status": "Resolved",
            "resolution": "Müşteriye modem konfigürasyon adımları iletildi, sorun çözüldü.",
        },
        {
            "subject": _("Fiber altyapı sorgulama sonucu alamıyorum"),
            "description": "Fiber Nerede uygulamasını kullanarak adresimi sorguladım ancak hiçbir sonuç gelmiyor. Fiber internet kullanmak istiyorum ama altyapı var mı yok mu öğrenemiyorum.",
            "category": "c3rcp5si0d",
            "priority": "Low",
            "communications": [
                {
                    "content": "Sayın müşterimiz,<br><br>Fiber Nerede uygulamasında verilen bilgiler periyodik olarak güncellenmektedir. Sorgulama anında altyapı bilgisi dönülemeyen adresler için size en yakın Türk Telekom ofislerine veya mağazalarına uğramanız gerekiyor.<br><br>Alternatif olarak:<br>- Türk Telekom Müşteri Hizmetleri: 444 1 444<br>- Online İşlemler üzerinden başvuru<br><br>Adresinizi paylaşırsanız, fiber altyapı durumunu kontrol edip size geri dönüş yapabiliriz.<br><br>Saygılarımla.",
                    "from_customer": False,
                },
                {
                    "content": "Teşekkürler, en yakın ofise gideceğim. Başka sorum olursa tekrar yazarım.",
                    "from_customer": True,
                },
            ],
            "status": "Resolved",
            "resolution": "Müşteriye Fiber Nerede uygulaması sınırlamaları açıklandı ve alternatif başvuru yolları gösterildi.",
        },
        {
            "subject": _("İnternet aboneliğimi feshetmek istiyorum"),
            "description": "Yurtdışına taşınacağım için internet aboneliğimi iptal etmek istiyorum. Nasıl bir prosedür uygulamam gerekiyor? Online yapabilir miyim?",
            "category": "c3rcp5si0d",
            "priority": "Medium",
            "communications": [
                {
                    "content": "Merhaba,<br><br>Evde internet abonelik iptal işlemlerinizi aşağıdaki yollarla gerçekleştirebilirsiniz:<br><br>1. Türk Telekom Online İşlem Merkezi üzerinden başvuru yaparak<br>2. Türk Telekom Ofis/Grup Mağazalarına şahsen başvuru yaparak<br>3. 0(312) 306 07 16 no'lu faksa kimlik belgesi ve imzalı dilekçe göndererek<br><br>Taahhüt durumunuzu kontrol etmeniz önemli. Taahhüt süreniz dolmadıysa cayma bedeli ödemeniz gerekebilir.<br><br>Detaylı bilgi için: <a href='/kb/c3sf1nlii3'>Fesih İşlemleri Hakkında</a><br><br>Başka sorunuz var mı?",
                    "from_customer": False,
                },
            ],
            "status": "Open",
            "resolution": "",
        },
        {
            "subject": _("Ev içi arıza tespiti için ücret alındı"),
            "description": "Teknik ekip evime geldi ve sorunun modemmis olduğunu söyledi. Ama bana 150 TL ücret çıkarttılar. Ben bunun ücretsiz olduğunu düşünüyordum?",
            "category": "c3rcp5si0d",
            "priority": "High",
            "communications": [
                {
                    "content": "Sayın müşterimiz,<br><br>Ev İçi Destek (Elitt) Hizmeti müşteri sorumluluğundaki konut/işyeri arızalarının tespiti için ücretsizdir.<br><br>Ancak:<br>- Teknik ekiplerin arızayı incelemesi sonucunda sorunun bina veya daire içindeki tesisat ya da modemle ilgili olduğu tespit edilirse<br>- Müşterimizin evinde inceleme yapılması/hizmet verilmesi için ücret alınmaktadır<br><br>Sizin durumunuzda modem arızalı bulunmuşsa ve yeni modem temin edildiyse, modem bedeli tahsil edilmiş olabilir.<br><br>Fatura detaylarınızı inceleyerek size geri dönüş yapayım mı?<br><br>Saygılarımla,<br>Müşteri Hizmetleri",
                    "from_customer": False,
                },
                {
                    "content": "Evet lütfen inceleyin. Modem değiştirildi ama bana ücretli olduğu önceden söylenmedi.",
                    "from_customer": True,
                },
            ],
            "status": "Open",
            "resolution": "",
        },
        {
            "subject": _("Nakil işlemi için gerekli belgeler neler?"),
            "description": "Yeni eve taşınacağım ve internet aboneliğimi de taşımak istiyorum. Hangi belgeleri hazırlayarak nereye başvurmam gerekiyor?",
            "category": "c3rcp5si0d",
            "priority": "Low",
            "communications": [
                {
                    "content": "Merhaba,<br><br>Evde internet nakil işlemleri için:<br><br><strong>Başvuru Yerleri:</strong><br>- En yakın Türk Telekom mağazaları<br>- Türk Telekom Çağrı Merkezi: 444 1 444<br><br><strong>Gerekli Belgeler:</strong><br>- Kimlik fotokopisi<br>- Yeni adres belgesi (fatura, ikamet belgesi vb.)<br>- Tapu fotokopisi veya kira sözleşmesi<br><br>Türk Telekom ev telefonu kullanan müşteriler, telefon nakli işlemleri için müşteri hizmetleri üzerinden ev telefonu nakil başvurusu yapabilir.<br><br>Detaylı bilgi: <a href='/kb/48aat8ss28'>Nakil İşlemi</a><br><br>İyi günler.",
                    "from_customer": False,
                },
                {
                    "content": "Teşekkürler, çok açıklayıcı oldu!",
                    "from_customer": True,
                },
            ],
            "status": "Resolved",
            "resolution": "Müşteriye nakil işlemi için başvuru yerleri ve gerekli belgeler detaylı şekilde açıklandı.",
        },
        {
            "subject": _("Paket değişikliği yapmak istiyorum ama taahhütlüyüm"),
            "description": "Mevcut 16 Mbps paketim var ve 50 Mbps'ye geçmek istiyorum. 6 aylık kampanya taahhüdüm var, daha 3 ay kaldı. Paket değiştirebilir miyim?",
            "category": "c3rcp5si0d",
            "priority": "Medium",
            "communications": [
                {
                    "content": "Sayın müşterimiz,<br><br>Kampanyalı (taahhütlü) müşteriler için paket değişikliği kuralları:<br><br>1. <strong>İndirim dönemi devam ediyorsa:</strong> Sadece kampanayla geldiğiniz paket veya daha üst paketlere geçiş yapabilirsiniz<br>2. <strong>İndirim dönemi bittiyse:</strong> Tüm paketlere geçiş yapabilirsiniz<br><br>Sizin durumunuzda taahhüt süreniz dolmadan daha üst pakete (50 Mbps) geçebilirsiniz. Ancak mevcut kampanya indiriminiz yeni pakette geçerli olmayabilir.<br><br>Paket değişikliği için:<br>- Online İşlemler: turktelekom.com.tr<br>- Müşteri Hizmetleri: 444 1 444<br>- Türk Telekom mağazaları<br><br>Daha fazla bilgi: <a href='/kb/db8v5qvh35'>Paket Değişikliği</a><br><br>Yardımcı olabilir miyim?",
                    "from_customer": False,
                },
                {
                    "content": "Anladım, yani daha hızlı pakete geçebilirim ama indirim olmayabilir. Önce fiyat teklifi alalım o zaman. Online İşlemler'den bakacağım, teşekkürler!",
                    "from_customer": True,
                },
            ],
            "status": "Resolved",
            "resolution": "Taahhütlü müşteri için paket değişikliği kuralları açıklandı, müşteri kendi başvuracak.",
        },
        {
            "subject": _("TekŞifre nedir ve nasıl kullanılır?"),
            "description": "Türk Telekom uygulamasına giriş yapmaya çalışıyorum ama 'TekŞifre ile giriş yapın' diyor. Bu nedir, nasıl alabilirim?",
            "category": "c3rcp5si0d",
            "priority": "Low",
            "communications": [
                {
                    "content": "Merhaba,<br><br><strong>TekŞifre Nedir?</strong><br>TekŞifre, Türk Telekom internet hizmetlerini çeşitli platformlardan kullanırken sizi tanımamızı sağlayan şifre uygulamasıdır. Tek bir şifre ile tüm Türk Telekom internet hizmetlerini kullanabilirsiniz.<br><br><strong>TekŞifre Nasıl Alınır?</strong><br>1. turktelekom.com.tr adresine gidin<br>2. Sağ üst köşedeki 'Giriş Yap' butonuna tıklayın<br>3. 'TekŞifre Oluştur' seçeneğine tıklayın<br>4. Telefon numaranıza gelen doğrulama kodunu girin<br>5. Yeni şifrenizi belirleyin<br><br><strong>Kullanım Alanları:</strong><br>- Online fatura sorgulama<br>- Kota sorgulama<br>- Paket değişikliği<br>- Mobil uygulamalar<br><br>Detaylı bilgi: <a href='/kb/at298dcedt'>Tek Şifre</a><br><br>Başka bir konuda yardımcı olabilir miyim?",
                    "from_customer": False,
                },
                {
                    "content": "Çok net açıkladınız, şimdi oluşturdum. Teşekkürler!",
                    "from_customer": True,
                },
            ],
            "status": "Resolved",
            "resolution": "TekŞifre tanımı ve oluşturma adımları müşteriye iletildi, sorun çözüldü.",
        },
        {
            "subject": _("Ödenmeyen fatura nedeniyle internet yavaşladı"),
            "description": "İnternetim çok yavaş, neredeyse hiçbir site açılmıyor. Faturamı geçen ay ödeyemedemedim, bu yüzden mi?",
            "category": "c3rcp5si0d",
            "priority": "High",
            "communications": [
                {
                    "content": "Sayın müşterimiz,<br><br>Evet, fatura borcunuzun son ödeme tarihinde ödenmemesi halinde hizmetiniz kısıtlanır.<br><br><strong>İnternet Kısıtlama Süreci:</strong><br>- Son ödeme tarihinden itibaren asgari 10 gün içinde bilgilendirme yapılır<br>- Hizmet kısıtlanması sonrası internet bağlantı hızı düşürülür<br>- Güvenlik sertifikalı siteler (https://) kısmen çalışmaya devam eder<br><br><strong>Çözüm:</strong><br>Faturanızı öderseniz 24 saat içinde hizmetiniz normale döner.<br><br><strong>Ödeme Kanalları:</strong><br>- Online İşlemler (kredi kartı/banka kartı)<br>- Türk Telekom mağazaları<br>- Anlaşmalı bankalar ve PTT<br>- Mobil ödeme uygulamaları<br><br>Güncel fatura borcunuz: [TUTAR] TL<br><br>Yardımcı olabilir miyim?",
                    "from_customer": False,
                },
            ],
            "status": "Open",
            "resolution": "",
        },
        {
            "subject": _("Yalın İnternet paketi telefon hattı olmadan alınır mı?"),
            "description": "Evimde sabit telefon kullanmıyorum, sadece internet istiyorum. Bu mümkün mü? Ayrı bir hat çekmem mi gerekiyor?",
            "category": "c3rcp5si0d",
            "priority": "Low",
            "communications": [
                {
                    "content": "Merhaba,<br><br>Evet, kesinlikle mümkün! <strong>Türk Telekom Yalın İnternet</strong> tam size göre.<br><br><strong>Yalın İnternet Avantajları:</strong><br>- Ev telefonu ve telefon hattı olmadan internet<br>- Sadece internet için ödeme yaparsınız<br>- ADSL altyapısı kullanılır<br>- Ayrı hat çekilmesine gerek yok<br><br><strong>Neler Yapabilirsiniz?</strong><br>- İhtiyaç duyduğunuz bilgiye anında ulaşmak<br>- Sosyal medya hesaplarınızda vakit geçirmek<br>- Tivibu Web'de sevdiğiniz programları izlemek<br>- Online alışveriş yapmak<br><br>Başvuru için:<br>- turktelekom.com.tr<br>- Müşteri Hizmetleri: 444 1 444<br>- Türk Telekom mağazaları<br><br>Detaylı bilgi: <a href='/kb/7bru4g1ldt'>Yalın İnternet</a><br><br>Hangi hız paketini tercih edersiniz?",
                    "from_customer": False,
                },
                {
                    "content": "Harika! 16 Mbps yeterli olur sanırım. Yarın mağazaya gideceğim, teşekkürler.",
                    "from_customer": True,
                },
                {
                    "content": "Rica ederim! Başvuru sırasında kimlik belgenizi ve adres belgenizi götürmeyi unutmayın. İyi günler!",
                    "from_customer": False,
                },
            ],
            "status": "Resolved",
            "resolution": "Müşteriye Yalın İnternet paketi hakkında detaylı bilgi verildi, başvuru için yönlendirildi.",
        },
        {
            "subject": _("Hat dondurma hizmeti nasıl kullanılır?"),
            "description": "3 ay yurtdışında olacağım. Bu süre zarfında internet aboneliğimi dondurup daha sonra devam ettirebilir miyim? Yoksa iptal edip dönünce yeniden mi başvurmalıyım?",
            "category": "c3rcp5si0d",
            "priority": "Medium",
            "communications": [
                {
                    "content": "Sayın müşterimiz,<br><br>Evet, <strong>Hat Dondurma Hizmeti</strong> tam ihtiyacınız olan hizmet!<br><br><strong>Hat Dondurma Nedir?</strong><br>İnternet erişimine geçici bir süre ihtiyaç duymayan müşterilerin ürünlerini dondurabilecekleri bir hizmettir.<br><br><strong>Önemli Bilgiler:</strong><br>- Minimum 1 ay, maksimum 6 ay süreyle dondurebilirsiniz<br>- Dondurma süresince aylık düşük bir ücret alınır (tam abonelik ücretinden çok daha az)<br>- Süre sonunda hizmetiniz otomatik devam eder<br>- Dondurma sırasında internet kullanılamaz<br><br><strong>Başvuru:</strong><br>- Türk Telekom Müşteri Hizmetleri: 444 1 444<br>- Online İşlemler üzerinden<br>- Türk Telekom mağazaları<br><br><strong>Önemli:</strong> Son ödeme tarihi geçmiş borcunuz varsa hat dondurma talebi karşılanmaz.<br><br>Detaylı bilgi: <a href='/kb/7pl46u0h69'>Hat Dondurma</a><br><br>Sizin için başvuru başlatayım mı?",
                    "from_customer": False,
                },
                {
                    "content": "Harika bir hizmet! Evet lütfen başvuru başlatın, 15 gün sonra yola çıkacağım.",
                    "from_customer": True,
                },
                {
                    "content": "Başvurunuz başlatıldı. Ödeme durumunuz kontrol edilip onaylandıktan sonra belirlediğiniz tarihte hizmet dondurulacak. Tahmini 2-3 iş günü içinde SMS ile bilgilendirme alacaksınız.<br><br>İyi yolculuklar!",
                    "from_customer": False,
                },
            ],
            "status": "Resolved",
            "resolution": "Hat dondurma hizmeti hakkında bilgi verildi ve müşteri adına başvuru başlatıldı.",
        },
    ]
    
    # Shuffle scenarios to randomize selection
    random.shuffle(scenarios)
    selected_scenarios = scenarios[:count]
    
    created_tickets = []
    
    for idx, scenario in enumerate(selected_scenarios):
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        creation_date = add_days(now_datetime(), -days_ago)
        
        # Create ticket
        ticket = frappe.get_doc({
            "doctype": "HD Ticket",
            "subject": scenario["subject"],
            "description": scenario["description"],
            "status": scenario["status"],
            "priority": scenario["priority"],
            "category": scenario.get("category"),
            "resolution": scenario.get("resolution", ""),
            "raised_by": customer_email,  # borovacihan@gmail.com as customer
            "_assign": agent_email,  # Administrator as agent
            "creation": creation_date,
            "modified": creation_date,
        })
        
        ticket.insert(ignore_permissions=True)
        
        # Create communications
        for comm_idx, comm in enumerate(scenario["communications"]):
            comm_date = add_days(creation_date, comm_idx * random.choice([0.5, 1, 2]))  # Space out communications
            
            communication = frappe.get_doc({
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "Email",
                "sent_or_received": "Received" if comm["from_customer"] else "Sent",
                "content": comm["content"],
                "reference_doctype": "HD Ticket",
                "reference_name": ticket.name,
                "sender": customer_email if comm["from_customer"] else agent_email,
                "creation": comm_date,
                "modified": comm_date,
            })
            
            communication.insert(ignore_permissions=True)
        
        # Update ticket modified date to last communication
        if scenario["communications"]:
            last_comm_date = add_days(creation_date, len(scenario["communications"]) - 1)
            frappe.db.set_value("HD Ticket", ticket.name, "modified", last_comm_date)
        
        created_tickets.append(ticket.name)
        print(f"✓ Created ticket {ticket.name}: {scenario['subject']}")
    
    frappe.db.commit()
    print(f"\n✅ Successfully created {len(created_tickets)} realistic tickets with communications")
    print(f"Ticket IDs: {', '.join(str(t) for t in created_tickets)}")
    
    return created_tickets


def update_ticket_statuses():
    """Update some tickets to Resolved status and add SLA/feedback data."""
    import random
    from frappe.utils import add_days, now_datetime, get_datetime
    
    # Get tickets that should be resolved (based on original scenarios)
    resolved_subjects = [
        "Modem kurulumu sırasında bağlantı problemi",
        "Fiber altyapı sorgulama sonucu alamıyorum",
        "Nakil işlemi için gerekli belgeler neler?",
        "Paket değişikliği yapmak istiyorum ama taahhütlüyüm",
        "TekŞifre nedir ve nasıl kullanılır?",
        "Hat dondurma hizmeti nasıl kullanılır?",
        "Yalın İnternet paketi telefon hattı olmadan alınır mı?",
    ]
    
    tickets = frappe.get_all(
        "HD Ticket",
        filters={"subject": ["in", resolved_subjects]},
        fields=["name", "creation", "subject"],
    )
    
    for ticket in tickets:
        # Update to Resolved
        frappe.db.set_value("HD Ticket", ticket.name, "status", "Resolved")
        
        # Set resolution time (2-48 hours after creation)
        resolution_hours = random.randint(2, 48)
        resolution_datetime = add_days(get_datetime(ticket.creation), resolution_hours / 24)
        frappe.db.set_value("HD Ticket", ticket.name, "resolution_date", resolution_datetime)
        
        # Add first response time (15 min to 2 hours in SECONDS, not minutes!)
        first_response_minutes = random.randint(15, 120)
        first_response_seconds = first_response_minutes * 60
        first_responded_datetime = add_days(get_datetime(ticket.creation), first_response_minutes / (24 * 60))
        
        frappe.db.set_value("HD Ticket", ticket.name, {
            "first_response_time": first_response_seconds,
            "first_responded_on": first_responded_datetime,
        })
        
        # Set SLA (80% fulfilled)
        response_by = add_days(get_datetime(ticket.creation), 1)  # 24 hour response SLA
        resolution_by = add_days(get_datetime(ticket.creation), 3)  # 72 hour resolution SLA
        
        # Check if SLA was met
        sla_fulfilled = first_response_seconds <= (24 * 3600) and resolution_hours <= 72
        agreement_status = "Fulfilled" if sla_fulfilled else "Failed"
        
        frappe.db.set_value("HD Ticket", ticket.name, {
            "response_by": response_by,
            "resolution_by": resolution_by,
            "agreement_status": agreement_status,
        })
        
        # Add feedback rating (0-1 scale where 1.0 = 5 stars)
        # Dashboard multiplies by 5, so 0.8 = 4 stars, 1.0 = 5 stars
        if random.random() < 0.9:  # 90% of resolved tickets have feedback
            star_rating = random.choice([3, 4, 4, 5, 5])  # Weighted towards 4-5
            feedback_rating = star_rating / 5.0  # Convert to 0-1 scale
            frappe.db.set_value("HD Ticket", ticket.name, "feedback_rating", feedback_rating)
        
        print(f"✓ Updated ticket {ticket.name}: {ticket.subject} → Resolved (SLA: {agreement_status})")
    
    frappe.db.commit()
    print(f"\n✅ Successfully updated {len(tickets)} tickets to Resolved status")
    
    return [t.name for t in tickets]


def fix_dashboard_metrics():
    """Fix all tickets with proper dashboard metrics."""
    import random
    from frappe.utils import add_days, get_datetime
    
    tickets = frappe.get_all(
        "HD Ticket",
        fields=["name", "creation", "status", "resolution_date"],
    )
    
    print(f"Fixing metrics for {len(tickets)} tickets...")
    
    for ticket in tickets:
        updates = {}
        
        # Set first_response_time and first_responded_on (15 min to 3 hours)
        first_response_minutes = random.randint(15, 180)
        first_response_seconds = first_response_minutes * 60
        first_responded_datetime = add_days(get_datetime(ticket.creation), first_response_minutes / (24 * 60))
        
        updates["first_response_time"] = first_response_seconds
        updates["first_responded_on"] = first_responded_datetime
        
        # Set SLA targets
        response_by = add_days(get_datetime(ticket.creation), 1)  # 24 hour response SLA
        resolution_by = add_days(get_datetime(ticket.creation), 3)  # 72 hour resolution SLA
        
        updates["response_by"] = response_by
        updates["resolution_by"] = resolution_by
        
        # Calculate SLA status (70% fulfilled rate)
        if ticket.status == "Resolved":
            # For resolved tickets, set resolution_time (4-48 hours in seconds)
            resolution_hours = random.randint(4, 48)
            resolution_seconds = resolution_hours * 3600
            resolution_datetime = add_days(get_datetime(ticket.creation), resolution_hours / 24)
            
            updates["resolution_date"] = resolution_datetime
            updates["resolution_time"] = resolution_seconds
            
            # SLA check: response < 24h and resolution < 72h
            sla_fulfilled = first_response_seconds <= (24 * 3600) and resolution_hours <= 72
            
            # Bias towards fulfilled (70%)
            if random.random() < 0.3:  # 30% chance to flip
                sla_fulfilled = not sla_fulfilled
            
            updates["agreement_status"] = "Fulfilled" if sla_fulfilled else "Failed"
            
            # Add feedback rating for 85% of resolved tickets (0-1 scale)
            if random.random() < 0.85:
                star_rating = random.choices([3, 4, 5], weights=[10, 40, 50])[0]  # Weighted: 10% 3-star, 40% 4-star, 50% 5-star
                updates["feedback_rating"] = star_rating / 5.0
        else:
            # Open tickets don't have SLA status yet
            updates["agreement_status"] = "Ongoing"
        
        frappe.db.set_value("HD Ticket", ticket.name, updates)
        print(f"  ✓ {ticket.name}: first_response={first_response_minutes}min, resolution={updates.get('resolution_time', 0) // 3600}h, SLA={updates.get('agreement_status', 'N/A')}")
    
    frappe.db.commit()
    print(f"\n✅ Successfully fixed metrics for {len(tickets)} tickets")
    print("Dashboard şimdi doğru değerler göstermeli:")
    print("  - Avg. First Response: ~1-2 saat")
    print("  - Avg. Resolution: ~1-2 gün")
    print("  - % SLA Fulfilled: ~70%")
    print("  - Avg. Feedback Rating: ~4.2/5")
    
    return len(tickets)


# -----------------------------
# AI backfill utilities (heuristic)
# -----------------------------
def _plain_text(html: str) -> str:
    """Convert HTML to plain text safely."""
    if not html:
        return ""
    try:
        from bs4 import BeautifulSoup  # dependency exists in app

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ")
        return " ".join(text.split())[:4000]
    except Exception:
        return html


def _analyze_sentiment(text: str) -> str:
    """Tiny lexicon-based sentiment: 'Olumlu' | 'Nötr' | 'Olumsuz'."""
    if not text:
        return "Nötr"
    t = text.lower()
    pos_words = {
        "tesekkur", "teşekkür", "harika", "mükemmel", "süper", "çalıştı", "çözüm", "great",
        "thanks", "thank you", "awesome", "works", "fixed", "+1", "👍", "😊", "😀", "mukemmel",
    }
    neg_words = {
        "hata", "çalışmıyor", "olmuyor", "sorun", "şikayet", "yavaş", "kötü", "rezalet", "berbat",
        "error", "fail", "doesn't", "broken", "slow", "angry", "-1", "👎", "😡", "😞",
    }
    pos = sum(1 for w in pos_words if w in t)
    neg = sum(1 for w in neg_words if w in t)
    if neg > pos + 1:
        return "Olumsuz"
    if pos > neg + 1:
        return "Olumlu"
    return "Nötr"


def _trend_from_series(sentiments: list[str]) -> str:
    """Return Turkish label trend to match UI helper mapping."""
    if not sentiments:
        return "Analiz ediliyor"
    score_map = {"Olumsuz": -1, "Nötr": 0, "Olumlu": 1}
    nums = [score_map.get(s, 0) for s in sentiments]
    if len(nums) < 2:
        return "Sabit"
    delta = nums[-1] - nums[0]
    variance = sum(abs(nums[i] - nums[i - 1]) for i in range(1, len(nums)))
    if delta > 0:
        return "İyileşiyor"
    if delta < 0:
        return "Kötüleşiyor"
    return "Sabit" if variance <= 1 else "Değişken"


def _effort_score(num_msgs: int, total_chars: int, resolution_hours: float | None, is_open: bool) -> int:
    """Compute 0-100 effort score from few signals."""
    msgs_component = min(num_msgs / 10.0, 1.0)  # up to 10 messages
    text_component = min(total_chars / 3000.0, 1.0)  # up to 3k chars
    if resolution_hours is not None:
        time_component = min(resolution_hours / 72.0, 1.0)  # cap at 72h
    else:
        time_component = 0.5
    base = 100 * (0.4 * msgs_component + 0.3 * text_component + 0.3 * time_component)
    if is_open:
        base += 7
    return int(max(0, min(100, round(base))))


def _effort_band(score: int) -> str:
    if score <= 33:
        return "Düşük"
    if score <= 66:
        return "Orta"
    return "Yüksek"


def _generate_summary(subject: str, first_msg: str, last_msg: str, status: str) -> str:
    first = (first_msg or "").strip()[:180]
    last = (last_msg or "").strip()[:180]
    parts = []
    if subject:
        parts.append(f"Konu: {subject}.")
    if first:
        parts.append(f"Müşteri bildirimi: {first}")
    if last and last != first:
        parts.append(f"Son durum: {last}")
    if status:
        parts.append(f"Durum: {status}.")
    return " \n".join(parts)[:1000]


def _generate_reply_suggestion(last_customer_msg: str, sentiment: str) -> str:
    greeting = "Merhaba,"
    closing = "Saygılarımızla, Destek Ekibi"
    tone = {
        "Olumlu": "yardımcı olmaya devam ediyoruz.",
        "Nötr": "konuyu netleştirip çözüm sunuyoruz.",
        "Olumsuz": "yaşadığınız sorunu hızlıca çözeceğiz.",
    }.get(sentiment or "Nötr")
    body_hint = last_customer_msg.strip()[:240] if last_customer_msg else ""
    body = (
        f"{greeting}\n\n{tone} Aşağıdaki adımları deneyebilir misiniz?\n"
        "1) Modemi/uygulamayı yeniden başlatın\n"
        "2) Ayarları varsayılan yapıp tekrar deneyin\n"
        "3) Devam ederse bize ekran görüntüsü/çıktı paylaşın\n\n"
    )
    if body_hint:
        body += f"Not: İletinizden anladığımız: '{body_hint}'.\n\n"
    return body + closing


def backfill_ticket_ai(limit: int | None = None, only_missing: bool = True):
    """Backfill AI fields for HD Ticket using simple heuristics.

    Args:
        limit: Process at most this many tickets (None = all)
        only_missing: If True, update only when the field is empty/NULL
    """
    from frappe.query_builder import DocType
    from frappe.query_builder.functions import Coalesce

    HDTicket = DocType("HD Ticket")
    Communication = DocType("Communication")

    missing_cond = (
        (Coalesce(HDTicket.last_sentiment, "") == "")
        | (Coalesce(HDTicket.sentiment_trend, "") == "")
        | (HDTicket.effort_score.isnull())
        | (Coalesce(HDTicket.effort_band, "") == "")
        | (Coalesce(HDTicket.ai_summary, "") == "")
        | (Coalesce(HDTicket.ai_reply_suggestion, "") == "")
    )

    q = (
        frappe.qb.from_(HDTicket)
        .select(
            HDTicket.name,
            HDTicket.subject,
            HDTicket.description,
            HDTicket.status,
            HDTicket.priority,
            HDTicket.resolution_time,
            HDTicket.last_sentiment,
            HDTicket.sentiment_trend,
            HDTicket.effort_score,
            HDTicket.effort_band,
            HDTicket.ai_summary,
            HDTicket.ai_reply_suggestion,
        )
    )
    if only_missing:
        q = q.where(missing_cond)
    if limit:
        q = q.limit(limit)

    rows = q.run(as_dict=True)
    print(f"Found {len(rows)} ticket(s) to backfill")

    updated = 0
    for row in rows:
        name = row["name"]
        comms = (
            frappe.qb.from_(Communication)
            .select(
                Communication.name,
                Communication.content,
                Communication.sent_or_received,
                Communication.creation,
            )
            .where(
                (Communication.reference_doctype == "HD Ticket")
                & (Communication.reference_name == name)
            )
            .orderby(Communication.creation)
        ).run(as_dict=True)

        texts = []
        sentiments_series = []
        last_customer_text = ""
        for c in comms:
            txt = _plain_text(c.get("content"))
            if txt:
                texts.append(txt)
                s = _analyze_sentiment(txt)
                sentiments_series.append(s)
                if (c.get("sent_or_received") or "").lower() == "received":
                    last_customer_text = txt

        if not texts:
            base_text = _plain_text(row.get("description")) or (row.get("subject") or "")
            if base_text:
                texts.append(base_text)
                sentiments_series.append(_analyze_sentiment(base_text))
                last_customer_text = base_text

        last_sentiment = row.get("last_sentiment") or _analyze_sentiment("\n".join(texts[-3:]))
        trend = row.get("sentiment_trend") or _trend_from_series(sentiments_series[-5:])

        resolution_seconds = row.get("resolution_time") or 0
        resolution_hours = (resolution_seconds or 0) / 3600.0 if resolution_seconds else None
        score = row.get("effort_score") or _effort_score(
            num_msgs=len(comms),
            total_chars=sum(len(t) for t in texts),
            resolution_hours=resolution_hours,
            is_open=(row.get("status") or "").lower() == "open",
        )
        band = row.get("effort_band") or _effort_band(int(score))

        ai_summary = row.get("ai_summary") or _generate_summary(
            row.get("subject") or "",
            texts[0] if texts else "",
            last_customer_text,
            row.get("status") or "",
        )
        ai_reply = row.get("ai_reply_suggestion") or _generate_reply_suggestion(
            last_customer_text, last_sentiment
        )

        updates = {}

        def need_set(key, value):
            if not value:
                return False
            if not only_missing:
                return True
            cur = row.get(key)
            if cur is None:
                return True
            if isinstance(cur, str) and cur.strip() == "":
                return True
            return False

        if need_set("last_sentiment", last_sentiment):
            updates["last_sentiment"] = last_sentiment
        if need_set("sentiment_trend", trend):
            updates["sentiment_trend"] = trend
        if need_set("effort_score", score):
            updates["effort_score"] = int(score)
        if need_set("effort_band", band):
            updates["effort_band"] = band
        if need_set("ai_summary", ai_summary):
            updates["ai_summary"] = ai_summary
        if need_set("ai_reply_suggestion", ai_reply):
            updates["ai_reply_suggestion"] = ai_reply

        if updates:
            frappe.db.set_value("HD Ticket", name, updates)
            updated += 1
            print(f"✓ Backfilled {name}: {list(updates.keys())}")

    frappe.db.commit()
    print(f"Done. Updated {updated} ticket(s)")
    return updated
