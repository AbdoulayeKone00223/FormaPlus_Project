"""Tests de la règle d'attestation (sans base de données)."""
import unittest
from decimal import Decimal

from certificates.rules import evaluer_conditions

PARAMS = dict(presence_min=80, note_min=10, paiement_obligatoire=True)


def cas(**kw):
    base = dict(taux=Decimal("100"), note=Decimal("12"), valide=False,
                reste=Decimal("0"), annulee=False)
    base.update(kw)
    return evaluer_conditions(**base, **PARAMS)


class RegleAttestationTests(unittest.TestCase):
    def test_tout_est_rempli(self):
        ok, raisons = cas()
        self.assertTrue(ok)
        self.assertEqual(raisons, [])

    def test_presence_insuffisante(self):
        ok, raisons = cas(taux=Decimal("66.7"))
        self.assertFalse(ok)
        self.assertEqual(len(raisons), 1)

    def test_presence_exactement_au_seuil(self):
        self.assertTrue(cas(taux=Decimal("80"))[0])

    def test_note_basse_sans_validation(self):
        self.assertFalse(cas(note=Decimal("9.99"))[0])

    def test_note_exactement_au_seuil(self):
        self.assertTrue(cas(note=Decimal("10"))[0])

    def test_note_basse_mais_validation_formateur(self):
        self.assertTrue(cas(note=Decimal("4"), valide=True)[0])

    def test_pas_de_note_mais_validation(self):
        self.assertTrue(cas(note=None, valide=True)[0])

    def test_pas_de_note_ni_validation(self):
        self.assertFalse(cas(note=None)[0])

    def test_paiement_incomplet(self):
        self.assertFalse(cas(reste=Decimal("1000"))[0])

    def test_paiement_non_obligatoire(self):
        ok, _ = evaluer_conditions(
            taux=Decimal("100"), note=Decimal("12"), valide=False, reste=Decimal("500"),
            annulee=False, presence_min=80, note_min=10, paiement_obligatoire=False,
        )
        self.assertTrue(ok)

    def test_inscription_annulee(self):
        self.assertFalse(cas(annulee=True)[0])

    def test_plusieurs_raisons(self):
        ok, raisons = cas(taux=Decimal("10"), note=None, reste=Decimal("5"))
        self.assertFalse(ok)
        self.assertEqual(len(raisons), 3)


if __name__ == "__main__":
    unittest.main()
