from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum, F
from .models import Item, Stock, StockCount, Supplier, PurchaseRequest
from .serializers import (
    ItemSerializer, StockSerializer, StockCountSerializer,
    SupplierSerializer, PurchaseRequestSerializer
)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        category = self.request.query_params.get('category', '')
        supplier = self.request.query_params.get('supplier', '')
        status = self.request.query_params.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_items = Item.objects.count()
        total_value = Stock.objects.aggregate(
            total=Sum(F('quantity') * F('item__unit_price'))
        )['total'] or 0
        low_stock = Stock.objects.filter(
            quantity__lte=F('item__reorder_point')
        ).count()
        
        return Response({
            'total_items': total_items,
            'total_value': total_value,
            'low_stock': low_stock
        })

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        item = self.request.query_params.get('item', '')
        location = self.request.query_params.get('location', '')
        
        if item:
            queryset = queryset.filter(item_id=item)
        
        if location:
            queryset = queryset.filter(location=location)
        
        return queryset

class StockCountViewSet(viewsets.ModelViewSet):
    queryset = StockCount.objects.all()
    serializer_class = StockCountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        item = self.request.query_params.get('item', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        
        if item:
            queryset = queryset.filter(item_id=item)
        
        if date_from:
            queryset = queryset.filter(count_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(count_date__lte=date_to)
        
        return queryset

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        status = self.request.query_params.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        supplier = self.request.query_params.get('supplier', '')
        status = self.request.query_params.get('status', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            queryset = queryset.filter(request_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(request_date__lte=date_to)
        
        return queryset
