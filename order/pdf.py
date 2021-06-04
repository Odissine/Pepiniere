from django.views.generic.detail import DetailView
from django_xhtml2pdf.views import PdfMixin
from .models import Commande


class ProductPdfView(PdfMixin, DetailView):
    model = Commande
    template_name = "product_pdf.html"