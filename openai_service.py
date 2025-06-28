import os
from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.function = [
            {
                "name": "gerenciar_pedido",
                "description": "Gerencia pedidos de entrega, incluindo solicitação, consulta de status e cancelamento.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acao": {
                            "type": "string",
                            "enum": [
                                "solicitar_entrega",
                                "consultar_status",
                                "cancelar_entrega",
                            ],
                            "description": "Ação que o usuário deseja",
                        },
                        "endereco": {
                            "type": "string",
                            "description": "Endereço da entrega (se aplicável)",
                        },
                        "bairro": {
                            "type": "string",
                            "description": "Bairro da entrega (se aplicável)",
                        },
                        "pago": {
                            "type": "boolean",
                            "description": "Se o pedido já está pago (se aplicável)",
                        },
                        "forma_pagamento": {
                            "type": "string",
                            "description": "Forma de pagamento na entrega (se não estiver pago)",
                        },
                        "justificativa": {
                            "type": "string",
                            "description": "Motivo do cancelamento (se aplicável)",
                        },
                    },
                    "required": ["acao"],
                },
            }
        ]

    def get_client(self):
        return self.client

    def get_chat_completion(self, messages: list) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            functions=self.function,
        )
        return response
