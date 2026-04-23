import re
import logging
from typing import Tuple, List, Optional
from atlas.config import CONFIG

class GuardrailsManager:
    """
    Gère les règles de sécurité et de filtrage (Guardrails) avant l'envoi au LLM.
    """
    def __init__(self):
        self.config = CONFIG.get("guardrails", {})
        self.enabled = self.config.get("enabled", True)
        
        # Patterns d'injection courants
        self.injection_patterns = [
            "ignore previous instructions",
            "ignore all previous instructions",
            "tu es maintenant",
            "oublie tes instructions",
            "<|system|>"
        ]
        
        # Regex pour carte bancaire (format basique : 16 chiffres avec ou sans espaces/tirets)
        self.cc_pattern = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b')

    def apply_guardrails(self, user_message: str) -> Tuple[bool, str, Optional[str]]:
        """
        Applique l'ensemble des règles sur le message utilisateur.
        Retourne (is_blocked, modified_message, block_reason).
        """
        if not self.enabled:
            return False, user_message, None

        # Règle 1 : Limitation de longueur
        max_words = self.config.get("max_words", 100)
        word_count = len(user_message.split())
        if word_count > max_words:
            reason = f"Requête trop longue ({word_count} mots). Maximum autorisé : {max_words} mots."
            return True, user_message, reason

        message_lower = user_message.lower()

        # Règle 2 : Blocage de sujets interdits
        blocked_topics = self.config.get("blocked_topics", [])
        for topic in blocked_topics:
            if topic.lower() in message_lower:
                reason = f"Sujet interdit détecté : {topic}"
                return True, user_message, reason

        # Règle 3 : Détection de prompt injection
        if self.config.get("prompt_injection_blocking", True):
            for pattern in self.injection_patterns:
                if pattern in message_lower:
                    reason = "Tentative d'injection de prompt détectée."
                    return True, user_message, reason

        # Règle 4 : Détection et masquage de PII (Carte Bancaire)
        modified_message = user_message
        if self.config.get("pii_masking", True):
            if self.cc_pattern.search(modified_message):
                modified_message = self.cc_pattern.sub("[MASKED_CC]", modified_message)
                
        return False, modified_message, None