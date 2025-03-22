from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages

class DeDuplicateMessagesMiddleware(MiddlewareMixin):
    """
    Middleware para evitar mensagens duplicadas.
    """
    def process_response(self, request, response):
        if hasattr(request, '_messages'):
            # Obter todas as mensagens
            storage = request._messages
            if storage is not None:
                # Extrair as mensagens atuais
                all_messages = list(storage)
                
                # Limpar todas as mensagens
                storage.used = True
                
                # Adicionar novamente apenas mensagens únicas
                seen = set()
                for message in all_messages:
                    # Criar uma chave única com o nível e texto da mensagem
                    key = (message.level, message.message)
                    if key not in seen:
                        seen.add(key)
                        # Readicionar a mensagem
                        level = message.level
                        messages.add_message(request, level, message.message)
                
        return response