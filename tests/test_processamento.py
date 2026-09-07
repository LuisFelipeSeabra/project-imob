import unittest
import os
import sys
from pathlib import Path

# Adicionar diretório scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from processar_fotos import validar_fotos, criar_diretorios

class TestProcessamentoFotos(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.test_dir = Path("./test_fotos")
        self.test_dir.mkdir(exist_ok=True)
        
        # Criar arquivos de teste
        for i in range(35):
            (self.test_dir / f"foto_{i:03d}.jpg").touch()
    
    def tearDown(self):
        """Limpeza após os testes"""
        if self.test_dir.exists():
            for arquivo in self.test_dir.glob("*"):
                arquivo.unlink()
            self.test_dir.rmdir()
    
    def test_validar_fotos_sucesso(self):
        """Testa validação com número suficiente de fotos"""
        fotos = validar_fotos(str(self.test_dir))
        self.assertEqual(len(fotos), 35)
        self.assertTrue(all(isinstance(f, Path) for f in fotos))
    
    def test_validar_fotos_insuficiente(self):
        """Testa validação com número insuficiente de fotos"""
        # Criar diretório com poucas fotos
        temp_dir = Path("./test_fotos_poucas")
        temp_dir.mkdir(exist_ok=True)
        
        for i in range(10):
            (temp_dir / f"foto_{i}.jpg").touch()
        
        fotos = validar_fotos(str(temp_dir))
        self.assertEqual(len(fotos), 0)
        
        # Limpar
        for arquivo in temp_dir.glob("*"):
            arquivo.unlink()
        temp_dir.rmdir()
    
    def test_criar_diretorios(self):
        """Testa criação de diretórios de trabalho"""
        criar_diretorios()
        self.assertTrue(Path("./output").exists())
        self.assertTrue(Path("./temp").exists())

if __name__ == '__main__':
    unittest.main()
