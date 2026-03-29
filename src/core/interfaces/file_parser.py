from abc import ABC, abstractmethod

class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Converte um arquivo em texto bruto."""
        pass
