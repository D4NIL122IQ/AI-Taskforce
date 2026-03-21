import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import back.models.agent
import back.models.message
import back.models.document
import back.models.workflow
import back.models.execution

import pytest
from back.models.etape import Etape


@pytest.fixture
def etape_valide():
    return Etape(ordre_execution=1, workflow_id=1)


class TestEtapeInit:

    def test_attributs_de_base(self, etape_valide):
        assert etape_valide.ordre_execution == 1
        assert etape_valide.workflow_id     == 1
        assert etape_valide.statut_etape    == "EN_ATTENTE"
        assert etape_valide.agent_id        is None

    def test_ordre_invalide(self):
        with pytest.raises(ValueError, match="ordre doit être >= 1"):
            Etape(ordre_execution=0, workflow_id=1)

    @pytest.mark.parametrize("ordre", [1, 5, 100])
    def test_ordres_valides(self, ordre):
        etape = Etape(ordre_execution=ordre, workflow_id=1)
        assert etape.ordre_execution == ordre


class TestEtapeDefinirEtape:

    def test_definir_etape(self, etape_valide):
        etape_valide.definirEtape("Analyser le code", agent_id=42)
        assert etape_valide.description_tache == "Analyser le code"
        assert etape_valide.agent_id          == 42

    def test_description_vide_leve_erreur(self, etape_valide):
        with pytest.raises(ValueError, match="Description de tâche vide"):
            etape_valide.definirEtape("", agent_id=1)


class TestEtapeModifierOrdre:

    def test_modifier_ordre_valide(self, etape_valide):
        etape_valide.modifierOrdre(3)
        assert etape_valide.ordre_execution == 3

    def test_modifier_ordre_invalide(self, etape_valide):
        with pytest.raises(ValueError, match="ordre doit être >= 1"):
            etape_valide.modifierOrdre(0)


class TestEtapeChangerStatut:

    def test_en_attente_vers_en_cours(self, etape_valide):
        etape_valide.changerStatut("EN_COURS")
        assert etape_valide.statut_etape == "EN_COURS"

    def test_en_cours_vers_termine(self, etape_valide):
        etape_valide.changerStatut("EN_COURS")
        etape_valide.changerStatut("TERMINE")
        assert etape_valide.statut_etape == "TERMINE"

    def test_en_cours_vers_erreur(self, etape_valide):
        etape_valide.changerStatut("EN_COURS")
        etape_valide.changerStatut("ERREUR")
        assert etape_valide.statut_etape == "ERREUR"

    def test_erreur_vers_en_attente_retry(self, etape_valide):
        etape_valide.changerStatut("EN_COURS")
        etape_valide.changerStatut("ERREUR")
        etape_valide.changerStatut("EN_ATTENTE")
        assert etape_valide.statut_etape == "EN_ATTENTE"

    def test_termine_est_terminal(self, etape_valide):
        etape_valide.changerStatut("EN_COURS")
        etape_valide.changerStatut("TERMINE")
        with pytest.raises(ValueError, match="Transition invalide"):
            etape_valide.changerStatut("EN_COURS")

    @pytest.mark.parametrize("depart,arrivee", [
        ("EN_ATTENTE", "TERMINE"),
        ("EN_ATTENTE", "ERREUR"),
        ("EN_COURS",   "EN_ATTENTE"),
        ("TERMINE",    "EN_ATTENTE"),
        ("TERMINE",    "ERREUR"),
    ])
    def test_transitions_interdites(self, depart, arrivee):
        etape = Etape(ordre_execution=1, workflow_id=1)
        etape.statut_etape = depart
        with pytest.raises(ValueError, match="Transition invalide"):
            etape.changerStatut(arrivee)

    def test_statut_inconnu_leve_erreur(self, etape_valide):
        with pytest.raises(ValueError, match="Statut inconnu"):
            etape_valide.changerStatut("INCONNU")


class TestEtapeToDict:

    def test_cles_presentes(self, etape_valide):
        d = etape_valide.toDict()
        assert set(d.keys()) == {
            "id_etape", "ordre_execution", "description_tache",
            "statut_etape", "agent_id", "workflow_id"
        }

    def test_valeurs_correctes(self, etape_valide):
        d = etape_valide.toDict()
        assert d["ordre_execution"] == 1
        assert d["statut_etape"]    == "EN_ATTENTE"
        assert d["agent_id"]        is None

    def test_repr(self, etape_valide):
        assert "EN_ATTENTE" in repr(etape_valide)