from django import forms
from .models import Contract, ContractClause, ContractPayment

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'title', 'description', 'contract_type',
            'project', 'client', 'start_date', 'end_date', 'signing_date',
            'total_value', 'advance_payment', 'retention_percentage',
            'contract_file', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'signing_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ContractClauseForm(forms.ModelForm):
    class Meta:
        model = ContractClause
        fields = [
            'title', 'content', 'order'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class ContractPaymentForm(forms.ModelForm):
    class Meta:
        model = ContractPayment
        fields = [
            'payment_number', 'payment_type', 'amount',
            'due_date', 'payment_date', 'notes', 'status'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
