"""Génération du PDF d'une attestation avec ReportLab."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

BLEU = colors.HexColor("#1F4E79")
GRIS = colors.HexColor("#555555")


def _date(d):
    return d.strftime("%d/%m/%Y")


def construire_pdf(
    *,
    apprenant,
    formation,
    centre,
    adresse_centre,
    date_debut,
    date_fin,
    duree_heures,
    lieu,
    reference,
    date_emission,
):
    """Retourne le contenu (bytes) du PDF de l'attestation."""
    largeur, hauteur = landscape(A4)
    tampon = BytesIO()
    c = canvas.Canvas(tampon, pagesize=(largeur, hauteur))
    c.setTitle(f"Attestation {reference}")
    c.setAuthor(centre)

    # Cadre double
    c.setStrokeColor(BLEU)
    c.setLineWidth(3)
    c.rect(1.2 * 28.35, 1.2 * 28.35, largeur - 2.4 * 28.35, hauteur - 2.4 * 28.35)
    c.setLineWidth(0.8)
    c.rect(1.5 * 28.35, 1.5 * 28.35, largeur - 3.0 * 28.35, hauteur - 3.0 * 28.35)

    x = largeur / 2
    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(x, hauteur - 90, centre)
    if adresse_centre:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 10)
        c.drawCentredString(x, hauteur - 106, adresse_centre)

    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(x, hauteur - 175, "ATTESTATION DE FORMATION")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 13)
    c.drawCentredString(x, hauteur - 225, "Le centre atteste que")

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(x, hauteur - 270, apprenant)

    c.setFont("Helvetica", 13)
    c.drawCentredString(x, hauteur - 310, "a suivi avec succès la formation")

    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 20)
    y = hauteur - 345
    for ligne in simpleSplit(formation, "Helvetica-Bold", 20, largeur - 200):
        c.drawCentredString(x, y, ligne)
        y -= 26

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 13)
    c.drawCentredString(
        x,
        y - 12,
        f"du {_date(date_debut)} au {_date(date_fin)} - {duree_heures} heures - {lieu}",
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 10)
    c.drawString(80, 80, f"Référence : {reference}")
    c.drawString(80, 66, f"Délivrée le {_date(date_emission)}")
    c.drawRightString(largeur - 80, 80, "La direction du centre")
    c.line(largeur - 240, 96, largeur - 80, 96)

    c.showPage()
    c.save()
    return tampon.getvalue()


def pdf_attestation(attestation):
    """PDF d'une instance d'Attestation."""
    inscription = attestation.inscription
    session = inscription.session
    formation = session.formation
    return construire_pdf(
        apprenant=inscription.apprenant.nom,
        formation=formation.titre,
        centre=formation.centre.nom,
        adresse_centre=formation.centre.adresse,
        date_debut=session.date_debut,
        date_fin=session.date_fin,
        duree_heures=formation.duree_heures,
        lieu=session.lieu,
        reference=attestation.reference,
        date_emission=attestation.date_emission,
    )
