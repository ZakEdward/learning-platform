from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    messege = f'Дорогой {order.first_name},\n\n' \
        f'Вы успешно разместили заказ.'\
        f'Ваш идентификатор заказа - это {order_id}.'
    mail_send = send_mail(subject, messege, 'admin@shop.com', [order.email])
    return mail_send
