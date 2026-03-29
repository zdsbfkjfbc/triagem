import os
from src.core.interfaces.file_parser import FileParser

class TXTParser(FileParser):
    def parse(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

class PyPDFParser(FileParser):
    def parse(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text_pages = []
            for page in doc:
                # O parâmetro "text" extrai texto plano, preservando melhor a ordem de leitura (colunas)
                page_text = page.get_text("text").strip()
                if page_text:
                    text_pages.append(page_text)
            
            doc.close()
            final_text = "\n".join(text_pages).strip()
            
            if not final_text:
                raise Exception("O PDF parece ser uma imagem ou está vazio (nenhum texto extraível via PyMuPDF).")
            
            return final_text
        except ImportError:
            raise ImportError("A biblioteca PyMuPDF (fitz) não foi detectada. Verifique se ela foi instalada no seu ambiente atual.")
        except Exception as e:
            raise RuntimeError(f"Erro ao processar o PDF com PyMuPDF: {str(e)}")

class UniversalParser(FileParser):
    """Facade that selects the correct parser based on file extension."""
    def __init__(self):
        self.txt_parser = TXTParser()
        self.pdf_parser = PyPDFParser()

    def parse(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.pdf_parser.parse(file_path)
        elif ext == ".txt":
            return self.txt_parser.parse(file_path)
        else:
            raise ValueError(f"Extensão de arquivo não suportada: {ext}")
