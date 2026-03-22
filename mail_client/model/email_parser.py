"""
Парсинг писем из формата MIME в объект EmailMessage.
"""

import email
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
import quopri
from typing import Optional, Tuple, List
from .email_message import EmailMessage

def decode_mime_header(header: Optional[str]) -> str:
    """
    Декодирует заголовок MIME (может быть закодирован в нескольких частях).
    
    Args:
        header: строка заголовка или None
        
    Returns:
        декодированная строка
    """
    if header is None:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            # Если кодировка не указана, пробуем utf-8
            encoding = encoding or 'utf-8'
            try:
                part = part.decode(encoding)
            except UnicodeDecodeError:
                part = part.decode('utf-8', errors='replace')
        result.append(str(part))
    return " ".join(result)

def parse_email(raw_email: bytes) -> EmailMessage:
    """
    Преобразует сырое письмо (RFC822) в объект EmailMessage.
    
    Args:
        raw_email: байтовое представление письма
        
    Returns:
        EmailMessage: заполненный объект
    """
    msg = email.message_from_bytes(raw_email)
    
    # Заголовки
    subject = decode_mime_header(msg.get("Subject"))
    from_ = decode_mime_header(msg.get("From"))
    to = decode_mime_header(msg.get("To"))
    cc = decode_mime_header(msg.get("Cc"))
    bcc = decode_mime_header(msg.get("Bcc"))
    date_str = msg.get("Date", "")
    
    # Парсим дату в читаемый формат
    try:
        date_obj = parsedate_to_datetime(date_str)
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        date = date_str
    
    # Тело письма
    body_text = ""
    body_html = ""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Вложение
            if "attachment" in content_disposition:
                filename = decode_mime_header(part.get_filename())
                data = part.get_payload(decode=True)
                attachments.append((filename, data, content_type))
                continue
            
            # Тело письма
            if content_type == "text/plain":
                charset = part.get_content_charset() or 'utf-8'
                try:
                    body_text = part.get_payload(decode=True).decode(charset, errors='replace')
                except LookupError:
                    body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
            elif content_type == "text/html":
                charset = part.get_content_charset() or 'utf-8'
                try:
                    body_html = part.get_payload(decode=True).decode(charset, errors='replace')
                except LookupError:
                    body_html = part.get_payload(decode=True).decode('utf-8', errors='replace')
    else:
        # Не multipart – просто текст
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body_text = msg.get_payload(decode=True).decode(charset, errors='replace')
            except LookupError:
                body_text = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        elif content_type == "text/html":
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body_html = msg.get_payload(decode=True).decode(charset, errors='replace')
            except LookupError:
                body_html = msg.get_payload(decode=True).decode('utf-8', errors='replace')
    
    return EmailMessage(
        from_=from_,
        to=to,
        cc=cc,
        bcc=bcc,
        subject=subject,
        date=date,
        body_text=body_text,
        body_html=body_html,
        attachments=attachments
    )