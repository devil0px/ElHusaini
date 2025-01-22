from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, F, Avg
from django.utils import timezone

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category, Supplier, Item, ItemSupplier, Stock, StockCount,
    PurchaseRequest, PurchaseRequestItem, Warranty, Maintenance,
    MaintenanceTask, SupplierEvaluation, InventoryAlert
)
from .serializers import (
    CategorySerializer, SupplierSerializer, ItemSerializer,
    ItemSupplierSerializer, StockSerializer, StockCountSerializer,
    PurchaseRequestSerializer, PurchaseRequestItemSerializer,
    WarrantySerializer, MaintenanceSerializer, MaintenanceTaskSerializer,
    SupplierEvaluationSerializer, InventoryAlertSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['commercial_record', 'tax_number']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        supplier = self.get_object()
        evaluations = supplier.evaluations.all()
        serializer = SupplierEvaluationSerializer(evaluations, many=True)
        return Response(serializer.data)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def stock_balance(self, request, pk=None):
        item = self.get_object()
        stock_in = Stock.objects.filter(
            item=item,
            transaction_type='in'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        stock_out = Stock.objects.filter(
            item=item,
            transaction_type='out'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        balance = stock_in - stock_out
        
        return Response({
            'item_id': item.id,
            'item_name': item.name,
            'current_balance': balance,
            'minimum_quantity': item.minimum_quantity,
            'reorder_point': item.reorder_point
        })

class ItemSupplierViewSet(viewsets.ModelViewSet):
    queryset = ItemSupplier.objects.all()
    serializer_class = ItemSupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'supplier', 'is_preferred']
    ordering_fields = ['price', 'lead_time_days']

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item', 'transaction_type', 'project', 'supplier']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['created_at']

class StockCountViewSet(viewsets.ModelViewSet):
    queryset = StockCount.objects.all()
    serializer_class = StockCountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'count_date']
    ordering_fields = ['count_date']

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project', 'supplier']
    search_fields = ['request_number', 'notes']
    ordering_fields = ['created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        purchase_request = self.get_object()
        if purchase_request.status != 'pending':
            return Response(
                {'detail': 'يمكن اعتماد الطلبات في حالة قيد الموافقة فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_request.status = 'approved'
        purchase_request.approved_by = request.user
        purchase_request.save()
        
        serializer = self.get_serializer(purchase_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        purchase_request = self.get_object()
        if purchase_request.status != 'pending':
            return Response(
                {'detail': 'يمكن رفض الطلبات في حالة قيد الموافقة فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_request.status = 'rejected'
        purchase_request.save()
        
        serializer = self.get_serializer(purchase_request)
        return Response(serializer.data)

class PurchaseRequestItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequestItem.objects.all()
    serializer_class = PurchaseRequestItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['purchase_request', 'item']

class WarrantyViewSet(viewsets.ModelViewSet):
    queryset = Warranty.objects.all()
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item', 'provider', 'status']
    search_fields = ['warranty_number', 'terms', 'coverage']
    ordering_fields = ['end_date']

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        days = int(request.query_params.get('days', 30))
        expiry_date = timezone.now().date() + timezone.timedelta(days=days)
        
        warranties = self.queryset.filter(
            status='active',
            end_date__lte=expiry_date
        )
        
        serializer = self.get_serializer(warranties, many=True)
        return Response(serializer.data)

class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item', 'maintenance_type', 'status', 'provider']
    search_fields = ['description', 'performed_by', 'notes']
    ordering_fields = ['scheduled_date']

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        maintenance = self.get_object()
        if maintenance.status != 'scheduled':
            return Response(
                {'detail': 'يمكن بدء الصيانة المجدولة فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        maintenance.status = 'in_progress'
        maintenance.start_date = timezone.now()
        maintenance.save()
        
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        maintenance = self.get_object()
        if maintenance.status != 'in_progress':
            return Response(
                {'detail': 'يمكن إكمال الصيانة قيد التنفيذ فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        maintenance.status = 'completed'
        maintenance.end_date = timezone.now()
        maintenance.save()
        
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTask.objects.all()
    serializer_class = MaintenanceTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['maintenance', 'is_completed']
    search_fields = ['description', 'notes']

class SupplierEvaluationViewSet(viewsets.ModelViewSet):
    queryset = SupplierEvaluation.objects.all()
    serializer_class = SupplierEvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['supplier', 'evaluation_date']
    ordering_fields = ['evaluation_date', 'overall_rating']

class InventoryAlertViewSet(viewsets.ModelViewSet):
    queryset = InventoryAlert.objects.all()
    serializer_class = InventoryAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'status', 'item']
    search_fields = ['message']
    ordering_fields = ['created_at']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        if alert.status != 'active':
            return Response(
                {'detail': 'يمكن معالجة التنبيهات النشطة فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        alert = self.get_object()
        if alert.status != 'active':
            return Response(
                {'detail': 'يمكن تجاهل التنبيهات النشطة فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'ignored'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # تطبيق الفلتر حسب الفئة
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # تطبيق البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # إضافة الرصيد الحالي لكل صنف
        for item in context['items']:
            stock_in = Stock.objects.filter(
                item=item,
                transaction_type='in'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            stock_out = Stock.objects.filter(
                item=item,
                transaction_type='out'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            item.current_balance = stock_in - stock_out
        
        return context

class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        
        # حساب إحصائيات المخزون
        stock_in = Stock.objects.filter(
            item=item,
            transaction_type='in'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        stock_out = Stock.objects.filter(
            item=item,
            transaction_type='out'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        context.update({
            'current_balance': stock_in - stock_out,
            'total_in': stock_in,
            'total_out': stock_out
        })
        
        return context

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'inventory/item_form.html'
    fields = ['code', 'name', 'description', 'category', 'unit', 'minimum_quantity', 
             'reorder_point', 'purchase_price', 'selling_price']
    success_url = reverse_lazy('inventory:item-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إضافة المنتج بنجاح.')
        return super().form_valid(form)

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'inventory/item_form.html'
    fields = ['code', 'name', 'description', 'category', 'unit', 'minimum_quantity', 
             'reorder_point', 'purchase_price', 'selling_price']
    
    def get_success_url(self):
        return reverse_lazy('inventory:item_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المنتج بنجاح.')
        return super().form_valid(form)

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('inventory:item-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المنتج بنجاح.')
        return super().delete(request, *args, **kwargs)

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # تطبيق البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # تطبيق فلتر الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(is_active=(status == 'active'))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # حساب متوسط التقييم لكل مورد
        for supplier in context['suppliers']:
            avg_rating = SupplierEvaluation.objects.filter(
                supplier=supplier
            ).aggregate(avg=Avg('rating'))['avg']
            supplier.average_rating = round(avg_rating, 1) if avg_rating else 0
        
        return context

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        
        # الأصناف التي يوردها
        context['items'] = supplier.items.all()
        
        # آخر التقييمات
        context['evaluations'] = SupplierEvaluation.objects.filter(
            supplier=supplier
        ).order_by('-created_at')[:5]
        
        # متوسط التقييم
        avg_rating = context['evaluations'].aggregate(avg=Avg('rating'))['avg']
        context['average_rating'] = round(avg_rating, 1) if avg_rating else 0
        
        # آخر طلبات الشراء
        context['purchase_requests'] = PurchaseRequest.objects.filter(
            supplier=supplier
        ).order_by('-created_at')[:5]
        
        return context

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    fields = ['code', 'name', 'contact_person', 'phone', 'email', 'address', 
             'tax_number', 'payment_terms', 'delivery_terms', 'notes', 'is_active']
    success_url = reverse_lazy('inventory:supplier_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إضافة المورد بنجاح.')
        return super().form_valid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    fields = ['code', 'name', 'contact_person', 'phone', 'email', 'address', 
             'tax_number', 'payment_terms', 'delivery_terms', 'notes', 'is_active']
    
    def get_success_url(self):
        return reverse_lazy('inventory:supplier_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المورد بنجاح.')
        return super().form_valid(form)

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('inventory:supplier_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المورد بنجاح.')
        return super().delete(request, *args, **kwargs)

class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_list.html'
    context_object_name = 'purchase_requests'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # تطبيق فلتر الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # تطبيق فلتر المورد
        supplier = self.request.GET.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # تطبيق فلتر التاريخ
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        return context

class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_detail.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.object
        
        # حساب الإجمالي
        total = sum(item.quantity * item.unit_price for item in request.items.all())
        context['total'] = total
        
        # التحقق من الصلاحيات
        user = self.request.user
        context['can_approve'] = user.has_perm('inventory.can_approve_purchase_request')
        context['can_edit'] = request.status == 'draft' and (
            user == request.created_by or 
            user.has_perm('inventory.change_purchaserequest')
        )
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        
        if action == 'approve' and request.user.has_perm('inventory.can_approve_purchase_request'):
            self.object.status = 'approved'
            self.object.approved_by = request.user
            self.object.approved_at = timezone.now()
            self.object.save()
            messages.success(request, 'تم الموافقة على طلب الشراء بنجاح.')
        
        elif action == 'reject' and request.user.has_perm('inventory.can_approve_purchase_request'):
            self.object.status = 'rejected'
            self.object.rejected_by = request.user
            self.object.rejected_at = timezone.now()
            self.object.rejection_reason = request.POST.get('rejection_reason')
            self.object.save()
            messages.success(request, 'تم رفض طلب الشراء.')
        
        elif action == 'complete' and self.object.status == 'approved':
            self.object.status = 'completed'
            self.object.completed_by = request.user
            self.object.completed_at = timezone.now()
            self.object.save()
            
            # إضافة الأصناف للمخزون
            for item in self.object.items.all():
                Stock.objects.create(
                    item=item.item,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    transaction_type='in',
                    reference_number=self.object.number,
                    notes=f'توريد من طلب الشراء رقم {self.object.number}',
                    created_by=request.user
                )
            
            messages.success(request, 'تم اكتمال طلب الشراء وإضافة الأصناف للمخزون.')
        
        return redirect('inventory:purchase_request_detail', pk=self.object.pk)

class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_form.html'
    fields = ['supplier', 'notes']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        response = super().form_valid(form)
        
        # إنشاء رقم تسلسلي للطلب
        year = timezone.now().year
        count = PurchaseRequest.objects.filter(created_at__year=year).count()
        form.instance.number = f'PR-{year}-{count+1:04d}'
        form.instance.save()
        
        messages.success(self.request, 'تم إنشاء طلب الشراء بنجاح.')
        return response

    def get_success_url(self):
        return reverse_lazy('inventory:purchase_request_detail', kwargs={'pk': self.object.pk})

class PurchaseRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseRequest
    template_name = 'inventory/purchase_request_form.html'
    fields = ['supplier', 'notes']
    
    def get_queryset(self):
        # السماح فقط بتعديل الطلبات في حالة مسودة
        return super().get_queryset().filter(status='draft')
    
    def get_success_url(self):
        return reverse_lazy('inventory:purchase_request_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث طلب الشراء بنجاح.')
        return super().form_valid(form)

class PurchaseRequestDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseRequest
    success_url = reverse_lazy('inventory:purchase_request_list')
    
    def get_queryset(self):
        # السماح فقط بحذف الطلبات في حالة مسودة
        return super().get_queryset().filter(status='draft')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف طلب الشراء بنجاح.')
        return super().delete(request, *args, **kwargs)

class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'inventory/maintenance_list.html'
    context_object_name = 'maintenance_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(item__name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(performed_by__icontains=search_query)
            )
        return queryset.order_by('-scheduled_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = Maintenance
    template_name = 'inventory/maintenance_detail.html'
    context_object_name = 'maintenance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.maintenancetask_set.all()
        return context

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    template_name = 'inventory/maintenance_form.html'
    fields = ['item', 'maintenance_type', 'description', 'scheduled_date', 'provider', 'estimated_cost']
    success_url = reverse_lazy('inventory:maintenance-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إنشاء عملية الصيانة بنجاح.')
        return super().form_valid(form)

class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    template_name = 'inventory/maintenance_form.html'
    fields = ['item', 'maintenance_type', 'description', 'scheduled_date', 'provider', 'estimated_cost', 'status']

    def get_success_url(self):
        return reverse_lazy('inventory:maintenance-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث عملية الصيانة بنجاح.')
        return super().form_valid(form)

class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Maintenance
    success_url = reverse_lazy('inventory:maintenance-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف عملية الصيانة بنجاح.')
        return super().delete(request, *args, **kwargs)

class AlertListView(LoginRequiredMixin, ListView):
    model = InventoryAlert
    template_name = 'inventory/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', 'active')
        if status == 'active':
            queryset = queryset.filter(status='active')
        elif status == 'resolved':
            queryset = queryset.filter(status='resolved')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(message__icontains=search_query) |
                Q(item__name__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'active')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class AlertDetailView(LoginRequiredMixin, DetailView):
    model = InventoryAlert
    template_name = 'inventory/alert_detail.html'
    context_object_name = 'alert'

class AlertResolveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        alert = get_object_or_404(InventoryAlert, pk=pk)
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        messages.success(request, 'تم حل التنبيه بنجاح.')
        return redirect('inventory:alert-list')

def dashboard(request):
    # إحصائيات سريعة
    total_items = Item.objects.count()
    pending_requests = PurchaseRequest.objects.filter(status='pending').count()
    scheduled_maintenance = Maintenance.objects.filter(status='scheduled').count()
    active_alerts = InventoryAlert.objects.filter(status='active').count()
    
    # الأصناف منخفضة المخزون
    low_stock_items = []
    for item in Item.objects.all():
        stock_in = Stock.objects.filter(
            item=item,
            transaction_type='in'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        stock_out = Stock.objects.filter(
            item=item,
            transaction_type='out'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        current_balance = stock_in - stock_out
        
        if current_balance <= item.minimum_quantity:
            low_stock_items.append({
                'id': item.id,
                'name': item.name,
                'current_balance': current_balance,
                'minimum_quantity': item.minimum_quantity
            })
    
    # الصيانة القادمة
    upcoming_maintenance = Maintenance.objects.filter(
        status='scheduled',
        scheduled_date__gte=timezone.now()
    ).order_by('scheduled_date')[:5]
    
    # آخر النشاطات (يمكن تنفيذها عندما نضيف نموذج للنشاطات)
    recent_activities = []
    
    context = {
        'total_items': total_items,
        'pending_requests': pending_requests,
        'scheduled_maintenance': scheduled_maintenance,
        'active_alerts': active_alerts,
        'low_stock_items': low_stock_items,
        'upcoming_maintenance': upcoming_maintenance,
        'recent_activities': recent_activities,
        'year': timezone.now().year
    }
    
    return render(request, 'inventory/dashboard.html', context)
