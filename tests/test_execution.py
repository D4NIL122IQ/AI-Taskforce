import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import back.models.agent
import back.models.message
import back.models.document
import back.models.workflow
import back.models.etape

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock
from back.models.execution import Execution, Resultat


@pytest.fixture
def execution_valide():
    return Execution(workflow_id=1)

@pytest.fixture
def resultat_valide():
    return Resultat(contenu_final="Synthèse finale.", execution_id=1)


# ==============================================================
# TESTS EXECUTION
# ==============================================================

class TestExecutionInit:

    def test_attributs_de_base(self, execution_valide):
        assert execution_valide.workflow_id  == 1
        assert execution_valide.status       == "EN_COURS"
        assert execution_valide.history_json == []
        assert execution_valide.outputs_json == {}

    def test_date_execution_auto(self, execution_valide):
        assert isinstance(execution_valide.date_execution, datetime)

    def test_date_execution_explicite(self):
        date = datetime(2024, 6, 1, tzinfo=timezone.utc)
        ex   = Execution(workflow_id=1, date_execution=date)
        assert ex.date_execution == date


class TestExecutionCollecterMessage:

    def test_collecter_message(self, execution_valide):
        mock_msg = MagicMock()
        execution_valide.messages = []
        execution_valide.collecterMessage(mock_msg)
        assert mock_msg in execution_valide.messages
        assert mock_msg.execution_id == execution_valide.id_execution

    def test_collecter_plusieurs_messages(self, execution_valide):
        execution_valide.messages = []
        for _ in range(3):
            execution_valide.collecterMessage(MagicMock())
        assert len(execution_valide.messages) == 3


class TestExecutionSauvegarderHistorique:

    def test_sauvegarde_history(self, execution_valide):
        mock_msg = MagicMock()
        mock_msg.toDict.return_value = {"contenu": "réponse"}
        execution_valide.sauvegarderHistorique({
            "history": ["step1", "step2"],
            "outputs": {1: mock_msg}
        })
        assert execution_valide.history_json == ["step1", "step2"]
        assert "1" in execution_valide.outputs_json

    def test_state_vide(self, execution_valide):
        execution_valide.sauvegarderHistorique({})
        assert execution_valide.history_json == []
        assert execution_valide.outputs_json == {}


class TestExecutionStatuts:

    def test_terminer(self, execution_valide):
        execution_valide.terminer()
        assert execution_valide.status == "TERMINE"

    def test_terminer_depuis_mauvais_statut(self, execution_valide):
        execution_valide.status = "TERMINE"
        with pytest.raises(ValueError, match="Impossible de terminer"):
            execution_valide.terminer()

    def test_marquer_erreur(self, execution_valide):
        execution_valide.marquerErreur()
        assert execution_valide.status == "ERREUR"

    def test_marquer_erreur_depuis_mauvais_statut(self, execution_valide):
        execution_valide.status = "TERMINE"
        with pytest.raises(ValueError, match="Impossible de marquer"):
            execution_valide.marquerErreur()


class TestExecutionTransmettreResultats:

    def test_sans_resultat(self, execution_valide):
        execution_valide.messages = []
        execution_valide.resultat = None
        d = execution_valide.transmettreResultats()
        assert d["status"]   == "EN_COURS"
        assert d["messages"] == []
        assert d["resultat"] is None

    def test_avec_resultat(self, execution_valide, resultat_valide):
        execution_valide.messages = []
        execution_valide.resultat = resultat_valide
        d = execution_valide.transmettreResultats()
        assert d["resultat"] is not None
        assert "contenu_final" in d["resultat"]

    def test_avec_messages(self, execution_valide):
        mock_msg = MagicMock()
        mock_msg.toDict.return_value = {"contenu": "test", "type": "agent_response"}
        execution_valide.messages = [mock_msg]
        execution_valide.resultat = None
        d = execution_valide.transmettreResultats()
        assert len(d["messages"]) == 1


class TestExecutionToDict:

    def test_cles_presentes(self, execution_valide):
        d = execution_valide.toDict()
        assert set(d.keys()) == {
            "id_execution", "date_execution", "status",
            "workflow_id", "history_json", "outputs_json"
        }

    def test_repr(self, execution_valide):
        assert "EN_COURS" in repr(execution_valide)


# ==============================================================
# TESTS RESULTAT
# ==============================================================

class TestResultatInit:

    def test_attributs_de_base(self, resultat_valide):
        assert resultat_valide.contenu_final == "Synthèse finale."
        assert resultat_valide.execution_id  == 1
        assert isinstance(resultat_valide.date_generation, datetime)

    def test_contenu_vide_leve_erreur(self):
        with pytest.raises(ValueError, match="Contenu final vide"):
            Resultat(contenu_final="", execution_id=1)

    def test_date_generation_explicite(self):
        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        r    = Resultat(contenu_final="ok", execution_id=1, date_generation=date)
        assert r.date_generation == date


class TestResultatExporter:

    def test_exporter_txt(self, resultat_valide):
        data = resultat_valide.exporter("txt")
        assert isinstance(data, bytes)
        assert "Synthèse".encode("utf-8") in data

    def test_exporter_json(self, resultat_valide):
        data   = resultat_valide.exporter("json")
        parsed = json.loads(data)
        assert "contenuFinal"   in parsed
        assert "dateGeneration" in parsed
        assert parsed["contenuFinal"] == "Synthèse finale."

    def test_exporter_format_invalide(self, resultat_valide):
        with pytest.raises(ValueError, match="Format non supporté"):
            resultat_valide.exporter("xlsx")


class TestResultatToDict:

    def test_cles_presentes(self, resultat_valide):
        d = resultat_valide.toDict()
        assert set(d.keys()) == {
            "id_resultat", "contenu_final", "date_generation", "execution_id"
        }

    def test_valeurs_correctes(self, resultat_valide):
        d = resultat_valide.toDict()
        assert d["contenu_final"] == "Synthèse finale."
        assert d["execution_id"]  == 1

    def test_repr(self, resultat_valide):
        assert "execution_id" in repr(resultat_valide)