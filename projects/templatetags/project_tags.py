from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(name='project_status_badge')
def project_status_badge(status):
    """
    Returns a Bootstrap badge with appropriate color for project status
    """
    status_classes = {
        'pending': 'bg-warning',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
        'on_hold': 'bg-secondary',
    }
    
    status_labels = {
        'pending': 'قيد الانتظار',
        'in_progress': 'قيد التنفيذ',
        'completed': 'مكتمل',
        'cancelled': 'ملغي',
        'on_hold': 'معلق',
    }
    
    css_class = status_classes.get(status, 'bg-secondary')
    label = status_labels.get(status, status)
    
    return mark_safe(f'<span class="badge {css_class}">{label}</span>')

@register.simple_tag(name='project_priority_badge')
def project_priority_badge(priority):
    """
    Returns a Bootstrap badge with appropriate color for project priority
    """
    priority_classes = {
        'low': 'bg-info',
        'medium': 'bg-warning',
        'high': 'bg-danger',
    }
    
    priority_labels = {
        'low': 'منخفض',
        'medium': 'متوسط',
        'high': 'عالي',
    }
    
    css_class = priority_classes.get(priority, 'bg-secondary')
    label = priority_labels.get(priority, priority)
    
    return mark_safe(f'<span class="badge {css_class}">{label}</span>')
