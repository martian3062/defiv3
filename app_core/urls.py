from django.urls import path
from . import views

urlpatterns = [
    # Wallet
    path("wallet/", views.wallet_page, name="wallet"),

    # Health
    path("healthz/", views.health_page, name="healthz"),
    path("healthz/data/", views.health_data, name="health_data"),

    # GROQ
    path("groq/test/ui/", views.groq_test_ui, name="groq_test_ui"),
    path("groq/test/", views.groq_test_ui, name="groq_test_alias"),  # 👈 alias
    path("groq/chat/", views.groq_chat_ui, name="groq_chat_ui"),
    path("groq/chat/ui/", views.groq_chat_ui, name="groq_chat_ui_alias"),  # 👈 alias
    path("api/groq/chat/", views.groq_chat_api, name="groq_chat_api"),

    # QuickNode simulate
    path("simulate/", views.simulate_page, name="simulate"),
    path("api/simulate/", views.simulate_api, name="simulate_api"),

    # Wallet QR
    path("wallet/qr/", views.wallet_qr_page, name="wallet_qr"),
    path("api/wallet/qr/", views.wallet_qr_api, name="wallet_qr_api"),

    # Health crypto data
    path("healthz/crypto_data/", views.crypto_latency_data, name="crypto_latency_data"),

    # Upcoming plans
    path("upcoming/", views.upcoming, name="upcoming"),
    path("upcoming/data/", views.upcoming_data, name="upcoming_data"),
]
