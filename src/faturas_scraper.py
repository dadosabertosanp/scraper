import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def main():
    print("🚀 Iniciando scraping de faturas ANP...")
    
    # === CONFIGURAÇÃO ===
    URL_FATURAS = "https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=[32205]"
    POST_URL = "https://contratos.comprasnet.gov.br/transparencia/faturas/search"
    
    # === SESSÃO ===
    s = requests.Session()
    
    # 1️⃣ GET inicial para pegar token CSRF
    r = s.get(URL_FATURAS)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
    print(f"🔑 CSRF token capturado: {csrf_token}")

    headers = {
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://contratos.comprasnet.gov.br",
        "Referer": URL_FATURAS,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Função para buscar faturas
    def buscar_faturas(start=0, length=100, draw=1):
        payload = {"draw": draw, "start": start, "length": length, "orgao": '["32205"]'}
        resp = s.post(POST_URL, data=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    # Cabeçalho da tabela
    CABECALHO = ["Órgão", "UG", "Fornecedor", "Contrato", "Fundamento Legal", 
                 "Objeto", "Observação", "Número da Fatura", "Data Emissão", 
                 "Data Recebimento", "Data Vencimento", "Data Pagamento", 
                 "Valor Original", "Retenção", "Glosa", "Deduções", "Valor Final", 
                 "Processo", "Data Referência", "Sub-Rogação", "Indício de Sobrepreço", 
                 "Mês", "Ano", "Situação", "Data Última Atualização"]

    # 2️⃣ Baixar todas as páginas
    print("📥 Baixando faturas da ANP...")
    todos_dados = []
    start = 0
    length = 100
    draw = 1

    while True:
        data = buscar_faturas(start=start, length=length, draw=draw)
        registros = data.get("data", [])
        if not registros:
            break

        for row in registros:
            linha_limpa = [BeautifulSoup(c, "html.parser").get_text(strip=True) for c in row]
            registro_dict = dict(zip(CABECALHO, linha_limpa))
            todos_dados.append(registro_dict)

        print(f"   ➝ Página {(start//length)+1}, registros: {len(registros)}")

        start += length
        draw += 1
        if len(registros) < length:
            break

    # 3️⃣ Salvar em JSON
    os.makedirs('data', exist_ok=True)
    arquivo_json = os.path.join('data', 'faturas_anp.json')
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump({
            "ultima_atualizacao": datetime.now().isoformat(),
            "total_registros": len(todos_dados),
            "dados": todos_dados
        }, f, ensure_ascii=False, indent=2)

    print(f"💾 JSON salvo em: {arquivo_json}")
    print(f"✅ Concluído! Total de registros: {len(todos_dados)}")
    return len(todos_dados)

if __name__ == "__main__":
    main()
