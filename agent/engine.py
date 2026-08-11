import json
import os

from openai import OpenAI

from skills.registry import ALL_TOOLS_SCHEMA, TOOL_MAPPING


class Agente:
    def __init__(
            self, 
            system_prompt: str = "Você é um assistente meteorológico útil e prestativo."
            ):
        
        self.client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )
        self.model_name = os.getenv("MODEL")
        self.historico = []

        if system_prompt:
            self.historico.append({"role": "system", "content": system_prompt})

    def executar(self, mensagem_usuario: str) -> str:
        self.historico.append(
            {
                "role": "user",
                "content": mensagem_usuario
            }
        )

        resposta = self.client.chat.completions.create(
            model = self.model_name,
            messages = self.historico,
            tools = ALL_TOOLS_SCHEMA
        )

        mensagem_ia = resposta.choices[0].message

        if mensagem_ia.tool_calls:
            self.historico.append(mensagem_ia)

            for chamada in mensagem_ia.tool_calls:
                nome_funcao = chamada.function.name
                argumentos = json.loads(chamada.function.arguments)

                funcao_para_rodar = TOOL_MAPPING.get(nome_funcao)
                if funcao_para_rodar:
                    resultado = funcao_para_rodar(**argumentos)

                    self.historico.append({
                        "role": "tool",
                        "tool_call_id": chamada.id,
                        "content": str(resultado)
                    })

            resposta_final = self.client.chat.completions.create(
                model = self.model_name,
                messages = self.historico
            )

            mensagem_final_ia = resposta_final.choices[0].message
            self.historico.append(mensagem_final_ia)
            return mensagem_final_ia.content

        self.historico.append(mensagem_ia)
        return mensagem_ia.content
