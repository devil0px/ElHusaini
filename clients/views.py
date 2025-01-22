from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Client, ClientContact
from .forms import ClientForm

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.object.contacts.all()
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'تم إنشاء العميل بنجاح.')
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def get_success_url(self):
        return reverse_lazy('clients:client-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث العميل بنجاح.')
        return super().form_valid(form)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('clients:client-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف العميل بنجاح.')
        return super().delete(request, *args, **kwargs)

class ContactListView(LoginRequiredMixin, ListView):
    model = ClientContact
    template_name = 'clients/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 10

    def get_queryset(self):
        return ClientContact.objects.filter(client_id=self.kwargs['client_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(pk=self.kwargs['client_pk'])
        return context

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = ClientContact
    template_name = 'clients/contact_detail.html'
    context_object_name = 'contact'

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = ClientContact
    template_name = 'clients/contact_form.html'
    fields = ['name', 'position', 'email', 'phone', 'notes']

    def form_valid(self, form):
        form.instance.client_id = self.kwargs['client_pk']
        messages.success(self.request, 'تم إضافة جهة الاتصال بنجاح.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clients:contact-list', kwargs={'client_pk': self.kwargs['client_pk']})

class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = ClientContact
    template_name = 'clients/contact_form.html'
    fields = ['name', 'position', 'email', 'phone', 'notes']

    def get_success_url(self):
        return reverse_lazy('clients:contact-list', kwargs={'client_pk': self.object.client.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث بيانات جهة الاتصال بنجاح.')
        return super().form_valid(form)

class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = ClientContact

    def get_success_url(self):
        return reverse_lazy('clients:contact-list', kwargs={'client_pk': self.object.client.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف جهة الاتصال بنجاح.')
        return super().delete(request, *args, **kwargs)
