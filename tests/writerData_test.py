# tests/test_writer_data.py
"""
Tests unitaires pour backend/modeles/writerData.py

Note : les fonctions writeAgent(), writeRespons() et writePrompt()
sont actuellement des stubs (retournent ""). Les tests documentent
le comportement attendu actuel et seront mis a jour quand
l implementation sera complete.

writeFile() a une erreur de syntaxe dans le code source (parenthese
manquante) — le test correspondant est marque xfail jusqu a correction.
"""

import pytest


class TestWriteAgent:

    def test_retourne_chaine(self):
        from backend.modeles.writerData import writeAgent
        result = writeAgent()
        assert isinstance(result, str)

    def test_retourne_valeur_vide_actuellement(self):
        from backend.modeles.writerData import writeAgent
        assert writeAgent() == ""


class TestWriteRespons:

    def test_retourne_chaine(self):
        from backend.modeles.writerData import writeRespons
        result = writeRespons()
        assert isinstance(result, str)

    def test_retourne_valeur_vide_actuellement(self):
        from backend.modeles.writerData import writeRespons
        assert writeRespons() == ""


class TestWritePrompt:

    def test_retourne_chaine(self):
        from backend.modeles.writerData import writePrompt
        result = writePrompt()
        assert isinstance(result, str)

    def test_retourne_valeur_vide_actuellement(self):
        from backend.modeles.writerData import writePrompt
        assert writePrompt() == ""


class TestWriteFile:

    @pytest.mark.xfail(
        reason="writeFile() a une erreur de syntaxe dans le source (parenthese manquante). "
               "A corriger dans writerData.py avant d activer ce test.",
        strict=True
    )
    def test_write_file_syntaxe_corrigee(self, tmp_path):
        """
        Ce test passera une fois que writeFile() sera implementee.
        Comportement attendu : cree un fichier au chemin donne.
        """
        from backend.modeles.writerData import writeFile
        filepath = str(tmp_path / "output.json")
        writeFile(filepath)
        import os
        assert os.path.exists(filepath)
