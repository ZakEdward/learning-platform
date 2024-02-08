import redis
from django.conf import settings
from .models import Product


r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class Recommeder:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'
    
    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # Получаем другие товары, купленные вместе
                if product_id != with_id:
                    # Увелтчиваем балл товара, купленного вм
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # Товар только 1
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 
                                   0, -1, desc=True)[:max_results]
        else:
            # генерируем временный ключ
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            # Объединяем товары и балы. Сохраняем во временном ключе
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # Удаляем id товаров к которым даём рекомендацию
            r.zrem(tmp_key, *product_ids)
            # Получаем id товаров по количеству и сортируем по -1 
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # Удаляем временный ключ
            r.delete(tmp_key)
        suggested_product_ids = [int(id) for id in suggestions]
        # Получаем рекомендуемые товары и сортируем их по порядку появления
        suggested_product = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_product.sort(key=lambda x: suggested_product_ids.index(x.id))
        return suggested_product
    
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))