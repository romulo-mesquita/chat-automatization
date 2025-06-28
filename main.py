from ast import arg
from openai_service import OpenAIService
import json


class Entrega:
    def __init__(
        self,
        acao,
        endereco=None,
        bairro=None,
        pago=None,
        forma_pagamento=None,
        justificativa=None,
    ):
        self.acao = acao
        self.endereco = endereco
        self.bairro = bairro
        self.pago = pago
        self.forma_pagamento = forma_pagamento
        self.justificativa = justificativa

    def __str__(self):
        return f"Entrega(acao={self.acao}, endereco={self.endereco}, bairro={self.bairro}, pago={self.pago}, forma_pagamento={self.forma_pagamento}, justificativa={self.justificativa})"


def interpreter_message(messagem, entrega):
    """
    Interprets a message and returns a response.

    Args:
        message (str): The message to interpret.

    Returns:
        str: The interpreted response.
    """
    chat_service = OpenAIService()

    try:
        with open("messages.json", "r", encoding="utf-8") as f:
            saved_messages = json.load(f)
    except FileNotFoundError:
        saved_messages = []
    except json.JSONDecodeError:
        print("Error decoding JSON from messages.json, starting with an empty list.")
        saved_messages = []
    if not saved_messages:
        saved_messages = [
            {
                "role": "system",
                "content": "Você é um assistente de pedidos de entrega. Identifique o que o cliente deseja fazer e colete as informações necessárias.",
            },
            {
                "role": "user",
                "content": messagem,
            },
        ]
    else:
        saved_messages.append({"role": "user", "content": messagem})
    response = chat_service.get_chat_completion(
        messages=saved_messages,
    )
    try:
        arguments = response.choices[0].message.function_call.arguments
    except AttributeError:
        arguments = None
    if response.choices[0].message.function_call:
        print("Função chamada:", response.choices[0].message.function_call.name)
        print(
            "Argumentos da função:", response.choices[0].message.function_call.arguments
        )
        entrega_data = json.loads(arguments)
        entrega = Entrega(
            acao=entrega_data.get("acao"),
            endereco=entrega_data.get("endereco"),
            bairro=entrega_data.get("bairro"),
            pago=entrega_data.get("pago"),
            forma_pagamento=entrega_data.get("forma_pagamento"),
            justificativa=entrega_data.get("justificativa"),
        )
        if entrega.acao == "solicitar_entrega":
            print("Ação: Solicitar entrega")
            print(f"Endereço: {entrega.endereco}")
            print(f"Bairro: {entrega.bairro}")
            confirmacao = input(
                "Confirma dados de endereço e bairro para entrega? (s/n): "
            )
            saved_messages.append(
                {
                    "role": "assistant",
                    "content": f"Endereço: {entrega.endereco}, Bairro: {entrega.bairro}. Confirma dados de endereço e bairro para entrega? (s/n):",
                }
            )
            if confirmacao.strip().lower() != "s":
                print("Entrega não confirmada. Por favor, revise as informações.")
                saved_messages = saved_messages + [
                    {
                        "role": "user",
                        "content": "n",
                    },
                    {
                        "role": "assistant",
                        "content": "Por favor, informe a informação correta do endereço e bairro.",
                    },
                ]
                return {"message": saved_messages[-1]["content"], "entrega": entrega}
            saved_messages.append(
                {
                    "role": "user",
                    "content": "s",
                },
            )

            if entrega.pago is None:
                forma_pagamento = input("A entrega já foi paga? (s/n): ")
                saved_messages.append(
                    {
                        "role": "user",
                        "content": "A entrega já foi paga? (s/n): ",
                    }
                )
                if forma_pagamento.strip().lower() == "n":
                    forma_pagamento = input("Informe a forma de pagamento na entrega: ")
                    entrega.forma_pagamento = forma_pagamento
                    saved_messages.append(
                        {
                            "role": "user",
                            "content": f"Forma de pagamento: {entrega.forma_pagamento}",
                        }
                    )
                else:
                    entrega.pago = True
                    saved_messages = saved_messages + [
                        {
                            "role": "user",
                            "content": "s",
                        },
                        {
                            "role": "assistant",
                            "content": "Solicitada com sucesso.",
                        },
                    ]
            print("Entrega solicitada com sucesso!")

        elif entrega.acao == "consultar_status":
            print("Ação: Consultar status da entrega")
            saved_messages.append(
                {
                    "role": "assistant",
                    "content": "Status da entrega consultado com sucesso!",
                }
            )
            print(f"Entrega: {entrega}")
    else:
        print("Resposta do assistente:", response.choices[0].message.content)
        saved_messages.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        )
    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(saved_messages, f, ensure_ascii=False, indent=2)
    return {"message": saved_messages[-1]["content"], "entrega": entrega}


def get_status_entrega(entrega):
    """
    Returns the status of the delivery.

    Args:
        entrega (Entrega): The delivery object.

    Returns:
        str: The status of the delivery.
    """
    if entrega.acao == "solicitar_entrega":
        return "Entrega solicitada com sucesso!"
    elif entrega.acao == "consultar_status":
        return "Status da entrega consultado com sucesso!"
    else:
        return "Ação desconhecida."


def main():
    entrega = Entrega(
        acao="inicio",
    )
    while True:
        user_message = input("Digite sua mensagem (ou 'parar' para encerrar): ")
        if user_message.strip().lower() == "parar":
            print("Encerrando o assistente.")
            break
        response = interpreter_message(user_message, entrega)
        print(response["message"])


if __name__ == "__main__":
    main()
