import requests
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# Asosiy ViewSet'lar
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# Telegram xabar yuborish endpoint'i
@api_view(['POST'])
def send_telegram_message(request):
    try:
        phone = request.data.get('phone')
        items = request.data.get('items', [])
        total = request.data.get('total')

        BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
        CHAT_ID = settings.TELEGRAM_CHAT_ID

        if not BOT_TOKEN or not CHAT_ID:
            return Response({'error': 'Telegram sozlamalari topilmadi'}, status=500)

        items_text = []
        for item in items:
            name = item.get('name', 'Noma\'lum')
            qty = int(item.get('quantity', 1))
            price = float(item.get('price', 0))
            total_item = price * qty
            items_text.append(f"• {name} x {qty} = {int(total_item)} so'm")
        
        items_str = "\n".join(items_text)
        message = (
            f"🛒 YANGI BUYURTMA!\n━━━━━━━━━━━━━━━━━━\n"
            f"📞 Telefon: {phone}\n\n📦 MAHSULOTLAR:\n{items_str}\n"
            f"━━━━━━━━━━━━━━━━━━\n💰 JAMI: {total} so'm"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code == 200:
            return Response({'status': 'ok'})
        else:
            # Telegram'dan qaytgan aniq xato sababini server logiga yozamiz
            # (Render'da: Dashboard -> Logs bo'limidan ko'rish mumkin)
            print(f"[TELEGRAM XATOSI] status={r.status_code} javob={r.text}")
            return Response({'error': 'Telegram xatosi', 'detail': r.text}, status=500)
    except Exception as e:
        print(f"[TELEGRAM ISTISNO] {e}")
        return Response({'error': str(e)}, status=500)