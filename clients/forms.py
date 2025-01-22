from django import forms
from .models import Client, ClientDocument, ClientContact

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name', 'client_type', 'contact_person', 'email',
            'phone', 'mobile', 'address', 'commercial_record',
            'tax_number', 'notes'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ['document_type', 'title', 'file', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ClientContactForm(forms.ModelForm):
    class Meta:
        model = ClientContact
        fields = ['name', 'position', 'email', 'phone', 'mobile', 'is_primary', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
