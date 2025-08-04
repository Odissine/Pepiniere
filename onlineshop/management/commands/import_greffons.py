import csv
from django.core.management.base import BaseCommand
from onlineshop.models import Greffons

class Command(BaseCommand):
    help = 'Importe les données greffons depuis un fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Chemin vers le fichier CSV')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    greffon_id = row.get('id')
                    if not greffon_id:
                        self.stderr.write("❌ Ligne sans ID, ignorée.")
                        continue

                    try:
                        greffon = Greffons.objects.get(id=greffon_id)
                        greffon.comm = int(row.get('Pré-Commandes') or 0)
                        greffon.greffons = int(row.get('Greffons') or 0)
                        greffon.objectif = int(row.get('Objectifs') or 0)
                        greffon.realise = int(row.get('Réalisés') or 0)
                        greffon.reussi = int(row.get('Réussis') or 0)
                        greffon.rang = int(row.get('Rangs') or 0)
                        greffon.save()
                        self.stdout.write(f"✔️ Greffon {greffon_id} mis à jour.")
                    except Greffons.DoesNotExist:
                        self.stderr.write(f"⚠️ Greffon {greffon_id} introuvable.")
                    except Exception as e:
                        self.stderr.write(f"❌ Erreur pour greffon {greffon_id} : {e}")
        except FileNotFoundError:
            self.stderr.write(f"❌ Fichier introuvable : {csv_path}")