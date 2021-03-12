from __future__ import unicode_literals

from django.forms import ModelForm
from django.forms.models import model_to_dict

from cspreports.models import CSPReport


class CSPReportForm(ModelForm):
    class Meta:
        model = CSPReport
        fields = '__all__'

    def __init__(self, message, *args, **kwargs):
        report = self._meta.model.from_message(message)
        super(CSPReportForm, self).__init__(model_to_dict(report), *args, **kwargs)
