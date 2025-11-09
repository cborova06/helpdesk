def is_email_content_empty(content: str | None) -> bool:
    return content is None or content.strip() == ""
    
def get_default_email_content(type: str) -> str:
    if type == "share_feedback":
        return """\
<p>Merhaba,</p>
<p>Bize ulaştığınız için teşekkür ederiz. #{{ doc.name }} numaralı destek deneyiminizle ilgili geri bildiriminizi almak isteriz.</p>
<a href="{{ url }}" class="btn btn-primary">Geri Bildirim Ver</a>

<p>Teşekkürler!<br>Destek Ekibi</p>"""

    if type == "acknowledgement":
        return """\
<p>Merhaba,</p>
<br />
<p>Bize ulaştığınız için teşekkür ederiz. Talebinizi aldık ve bir destek bileti oluşturduk.</p>
<p>
    <strong>Bilet ID:</strong> {{ doc.name }}<br />
    <strong>Konu:</strong> {{ doc.subject }}<br />
</p>
<p>Ekibimiz talebinizi inceliyor ve kısa süre içinde size geri dönecek.</p>
<br />
<p>Saygılarımızla,<br />Destek Ekibi</p>
"""

    if type == "reply_to_agents":
        return """\
<div>
  <p>Merhaba,</p>
  <p><strong>#{{ doc.name }}</strong> numaralı bilet için yeni bir yanıtınız var.</p>
  <p><strong>Konu:</strong> {{ doc.subject }}</p>
  <p><strong>Gönderen:</strong> {{ doc.raised_by }}</p>
  <p><strong>Öncelik:</strong> {{ doc.priority }}</p>

  <br />
  <p>
    Bu bileti görüntülemek ve yanıtlamak için
    <a href="{{ ticket_url }}">buraya tıklayın</a>.
  </p>
  <p>Saygılarımızla,<br />Destek Ekibi</p>
</div>
"""

    if type == "reply_via_agent":
        return """\
<div>
  <h2><strong>Bilet #{{ doc.name }}</strong></h2>
  <h3>Bu bilet için yeni bir yanıtınız var</h3>
  <br />
  <div style="margin-bottom: 10px">
    <h3 style="margin-bottom: 20px">Mesaj</h3>
    <div
      style="
        background: #f3f5f8;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #e5e9ee;
      "
    >
      {{ message }}
    </div>
  </div>
  <p>Bu mesaja yanıt vermek için lütfen müşteri portalını ziyaret edin</p>
  <a
    class="btn btn-primary"
    href="{{ ticket_url }}"
    rel="noopener noreferrer"
    target="_blank"
  >Portalda Görüntüle</a>
  <br />
</div>
"""
