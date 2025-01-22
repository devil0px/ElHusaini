from rest_framework import serializers
from .models import (
    Category, Supplier, Item, ItemSupplier, Stock, StockCount,
    PurchaseRequest, PurchaseRequestItem, Warranty, Maintenance,
    MaintenanceTask, SupplierEvaluation, InventoryAlert
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class ItemSupplierSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = ItemSupplier
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    suppliers = ItemSupplierSerializer(source='itemsupplier_set', many=True, read_only=True)
    
    class Meta:
        model = Item
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Stock
        fields = '__all__'

class StockCountSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = StockCount
        fields = '__all__'

class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = PurchaseRequestItem
        fields = '__all__'

class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseRequestItemSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = '__all__'

class WarrantySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = Warranty
        fields = '__all__'

class MaintenanceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = '__all__'

class MaintenanceSerializer(serializers.ModelSerializer):
    tasks = MaintenanceTaskSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = Maintenance
        fields = '__all__'

class SupplierEvaluationSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierEvaluation
        fields = '__all__'

class InventoryAlertSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = InventoryAlert
        fields = '__all__'
