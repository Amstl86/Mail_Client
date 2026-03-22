"""
Модель письма. Содержит все данные, необходимые для отображения и отправки.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class EmailMessage:
    """Представляет электронное письмо."""
    
    # Идентификатор письма на сервере (UID)
    uid: Optional[str] = None
    
    # Поля заголовка
    from_: str = ""
    to: str = ""
    cc: str = ""
    bcc: str = ""
    subject: str = ""
    date: str = ""
    
    # Тело письма (текст и HTML)
    body_text: str = ""
    body_html: str = ""
    
    # Вложения: список кортежей (имя_файла, данные, mime_type)
    attachments: List[Tuple[str, bytes, str]] = field(default_factory=list)
    
    # Флаг, прочитано ли письмо
    is_seen: bool = False
    
    def has_attachments(self) -> bool:
        """Возвращает True, если есть вложения."""
        return len(self.attachments) > 0
    
    def summary(self) -> str:
        """Краткое представление письма для списка."""
        return f"{self.date} | {self.from_} | {self.subject}"