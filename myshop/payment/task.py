from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_completed(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Мой магазин - Invoice no. {order.id}'
    messege = 'Пожалуйста, ознакомьтесь с прилагаемым счетом-фактурой за вашу недавнюю покупку.'
    email = EmailMessage(subject, messege, 'admin@myshop.com', [order.email])

    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    email.attach(f'order_{order_id}.pdf', out.getvalue(), 'application/pdf')
    email.send()