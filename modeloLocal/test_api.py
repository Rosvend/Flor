import requests

BASE_URL = "http://localhost:8000"

def test_flow(text, label=""):
    print(f"\n{'='*50}")
    print(f"PRUEBA: {label}")
    print(f"Texto: {text}")
    print(f"{'='*50}")
    
    try:
        response = requests.post(f"{BASE_URL}/process_pqrs", json={"text": text})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sentimiento: {data['sentiment']}")
            print(f"🔍 ¿Ofensivo?: {'SÍ ⚠️' if data['is_offensive'] else 'NO ✔️'}")
            if data['toxicity_warning']:
                print(f"⚠️  {data['toxicity_warning']}")
            print(f"\nRedacción mejorada:\n{data['improved_text'][:300]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Caso 1: Texto respetuoso
    test_flow(
        "Quisiera saber por qué no me han dado respuesta a mi solicitud del mes pasado.",
        "Texto Respetuoso"
    )
    
    # Caso 2: Texto con groserías
    test_flow(
        "Son unos inútiles de mierda, llevo meses esperando y nadie hace un carajo.",
        "Texto con Groserías"
    )
