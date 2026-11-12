"""Règles d'obtention d'une attestation (fonction pure, sans dépendance à Django)."""


def evaluer_conditions(
    *,
    taux,
    note,
    valide,
    reste,
    annulee,
    presence_min,
    note_min,
    paiement_obligatoire,
):
    """Retourne (eligible, raisons_de_refus).

    - taux : taux de présence en % ;
    - note : note sur 20 ou None ;
    - valide : validation manuelle par le formateur ;
    - reste : montant restant à payer ;
    - annulee : l'inscription est annulée.
    """
    raisons = []
    if annulee:
        raisons.append("Inscription annulée.")
    if taux < presence_min:
        raisons.append(f"Présence insuffisante ({taux:.0f} % pour {presence_min} % requis).")
    if not (valide or (note is not None and note >= note_min)):
        raisons.append(f"Note inférieure à {note_min}/20 et pas de validation du formateur.")
    if paiement_obligatoire and reste > 0:
        raisons.append(f"Paiement incomplet (reste {reste}).")
    return (not raisons, raisons)
