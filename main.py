from dotenv import load_dotenv

from agent.engine import Agente

load_dotenv()

if __name__ == "__main__":
    print("--- Agente de IA Iniciado (Com Memória) ---")

    agente = Agente()

    while True:
        prompt = input("\nVocê: ")
        if prompt.lower() in ["sair", "exit"]:
            break

        resposta = agente.executar(prompt)
        print(f"Agente: {resposta}")