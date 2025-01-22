from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

app_name = 'inventory'

# إنشاء router للـ API
router = DefaultRouter()
router.register(r'items', api.ItemViewSet)
router.register(r'stock', api.StockViewSet)
router.register(r'stock-counts', api.StockCountViewSet)
router.register(r'suppliers', api.SupplierViewSet)
router.register(r'purchase-requests', api.PurchaseRequestViewSet)

urlpatterns = [
    # مسارات API
    path('api/', include(router.urls)),
    
    # لوحة التحكم
    path('', views.dashboard, name='dashboard'),
    
    # المنتجات
    path('items/', views.ItemListView.as_view(), name='item-list'),
    path('items/create/', views.ItemCreateView.as_view(), name='item-create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),
    path('items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item-update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
    
    # الموردين
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),
    
    # طلبات الشراء
    path('purchase-requests/', views.PurchaseRequestListView.as_view(), name='purchase-request-list'),
    path('purchase-requests/create/', views.PurchaseRequestCreateView.as_view(), name='purchase-request-create'),
    path('purchase-requests/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='purchase-request-detail'),
    path('purchase-requests/<int:pk>/update/', views.PurchaseRequestUpdateView.as_view(), name='purchase-request-update'),
    path('purchase-requests/<int:pk>/delete/', views.PurchaseRequestDeleteView.as_view(), name='purchase-request-delete'),
    
    # الصيانة
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance-list'),
    path('maintenance/create/', views.MaintenanceCreateView.as_view(), name='maintenance-create'),
    path('maintenance/<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenance/<int:pk>/update/', views.MaintenanceUpdateView.as_view(), name='maintenance-update'),
    path('maintenance/<int:pk>/delete/', views.MaintenanceDeleteView.as_view(), name='maintenance-delete'),
    
    # التنبيهات
    path('alerts/', views.AlertListView.as_view(), name='alert-list'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    path('alerts/<int:pk>/resolve/', views.AlertResolveView.as_view(), name='alert-resolve'),
]
