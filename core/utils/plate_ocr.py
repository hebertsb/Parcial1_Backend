import cv2
import numpy as np
import pytesseract
import re
from typing import List, Tuple
from pytesseract import Output, TesseractError, TesseractNotFoundError


class PlateOCRException(Exception):
    """Errores específicos al procesar OCR de placas."""


PLATE_REGEX = re.compile(r'^\d{3,4}[A-Z]{3}$')


class PlateOCRService:
    """Servicio utilitario para detectar placas bolivianas a partir de una imagen."""

    PSM_CONFIG = '--psm 6'
    WHITELIST = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    @classmethod
    def extract_plate_candidates(cls, image_bytes: bytes) -> Tuple[List[str], str]:
        """Devuelve una lista de posibles placas y el texto crudo detectado."""
        image = cls._load_image(image_bytes)
        processed = cls._preprocess(image)

        raw_outputs: List[str] = []
        candidates: List[str] = []

        for img in (processed, image):
            text, words = cls._run_ocr(img)
            if text:
                raw_outputs.append(text)
            for token in cls._generate_combinations(words):
                normalized = cls._normalize_plate(token)
                if normalized:
                    candidates.append(normalized)

        unique_candidates = cls._unique_preserve_order(candidates)
        raw_text = ' '.join(out.strip() for out in raw_outputs if out.strip())
        return unique_candidates, raw_text

    @staticmethod
    def _load_image(image_bytes: bytes) -> np.ndarray:
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise PlateOCRException('No se pudo decodificar la imagen recibida.')
        return image

    @staticmethod
    def _preprocess(image: np.ndarray) -> np.ndarray:
        """Aplica transformaciones suaves para resaltar caracteres de la placa."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @classmethod
    def _run_ocr(cls, image: np.ndarray) -> Tuple[str, List[str]]:
        config = f"{cls.PSM_CONFIG} {cls.WHITELIST}".strip()
        try:
            text = pytesseract.image_to_string(image, config=config)
            data = pytesseract.image_to_data(image, output_type=Output.DICT, config=config)
        except (TesseractError, TesseractNotFoundError) as exc:
            raise PlateOCRException(f'Error ejecutando Tesseract: {exc}') from exc

        words = [w for w in data.get('text', []) if w]
        if not words:
            words = [token for token in re.split(r'\s+', text) if token]
        return text, words

    @staticmethod
    def _generate_combinations(words: List[str]) -> List[str]:
        combos: List[str] = []
        length = len(words)
        for idx in range(length):
            current = words[idx]
            combos.append(current)
            if idx + 1 < length:
                combos.append(current + words[idx + 1])
            if idx + 2 < length:
                combos.append(current + words[idx + 1] + words[idx + 2])
        return combos

    @staticmethod
    def _normalize_plate(token: str) -> str | None:
        cleaned = re.sub(r'[^A-Z0-9]', '', token.upper())
        if len(cleaned) not in (6, 7):
            return None

        # Determinar si la placa tiene 3 o 4 dígitos iniciales
        possible_lengths = (4, 3) if len(cleaned) == 7 else (3,)
        for digit_length in possible_lengths:
            digits = cleaned[:digit_length]
            letters = cleaned[digit_length:]
            digits = PlateOCRService._normalize_digits(digits)
            letters = PlateOCRService._normalize_letters(letters)
            candidate = digits + letters
            if PLATE_REGEX.match(candidate):
                return candidate
        return None

    @staticmethod
    def _normalize_digits(digits: str) -> str:
        substitutions = {
            'O': '0',
            'Q': '0',
            'D': '0',
            'I': '1',
            'L': '1',
            'Z': '2',
            'S': '5',
            'B': '8'
        }
        normalized = ''.join(substitutions.get(char, char) for char in digits)
        return normalized if normalized.isdigit() else digits

    @staticmethod
    def _normalize_letters(letters: str) -> str:
        substitutions = {
            '0': 'O',
            '1': 'I',
            '2': 'Z',
            '5': 'S',
            '6': 'G',
            '8': 'B'
        }
        normalized = ''.join(substitutions.get(char, char) for char in letters)
        return normalized if normalized.isalpha() else letters

    @staticmethod
    def _unique_preserve_order(items: List[str]) -> List[str]:
        seen = set()
        unique: List[str] = []
        for item in items:
            if item not in seen:
                unique.append(item)
                seen.add(item)
        return unique