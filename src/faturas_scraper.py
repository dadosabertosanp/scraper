import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def main():
    print("🚀 Iniciando scraping de faturas ANP...")
    
    try:
        # === CONFIGURAÇÃO ===
        URL_FATURAS = "https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=[32205]"
        POST_URL = "https://contratos.comprasnet.gov.br/transparencia/faturas/search"
        
        # === SESSÃO ===
        s = requests.Session()
        
        # 1️⃣ GET inicial para pegar token CSRF
        print("🔑 Obtendo token CSRF...")
        r = s.get(URL_FATURAS, timeout=30)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
        print(f"✅ CSRF token capturado: {csrf_token[:20]}...")

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
            payload = {
                "draw": draw,
                "start": start,
                "length": length,
                "orgao": '["32205"]'
            }
            resp = s.post(POST_URL, data=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()

        # Cabeçalho da tabela
        CABECALHO = [
            "Órgão", "UG", "Fornecedor", "Contrato", "Fundamento Legal", 
            "Objeto", "Observação", "Número da Fatura", "Data Emissão", 
            "Data Recebimento", "Data Vencimento", "Data Pagamento", 
            "Valor Original", "Retenção", "Glosa", "Deduções", "Valor Final", 
            "Processo", "Data Referência", "Sub-Rogação", "Indício de Sobrepreço", 
            "Mês", "Ano", "Situação", "Data Última Atualização"
        ]

        # Função para limpar HTML
        def limpar_html(texto):
            return BeautifulSoup(texto, "html.parser").get_text(strip=True)

        # 2️⃣ Baixar todas as páginas
        print("📥 Baixando faturas da ANP...")
        todos_dados = []
        start = 0
        length = 100
        draw = 1
        max_pages = 50  # limite de segurança

        while True:
            print(f"📄 Buscando página {(start//length)+1}...")
            data = buscar_faturas(start=start, length=length, draw=draw)
            registros = data.get("data", [])
            
            if not registros:
                print("✅ Nenhum registro adicional encontrado.")
                break

            # Processar registros
            for row in registros:
                linha_limpa = [limpar_html(celula) for celula in row]
                registro_dict = dict(zip(CABECALHO, linha_limpa))
                todos_dados.append(registro_dict)

            print(f"   ➝ Página {(start//length)+1}, registros: {len(registros)}")
            print(f"   ➝ Total acumulado: {len(todos_dados)} registros")

            # Próxima página
            start += length
            draw += 1
            
            # Limite de segurança para evitar loop infinito
            if len(registros) < length or (start//length) >= max_pages:
                print("✅ Todas as páginas percorridas.")
                break

        # 3️⃣ Salvar em JSON
        os.makedirs('data', exist_ok=True)
        arquivo_json = os.path.join('data', 'faturas_anp.json')
        
        resultado = {
            "ultima_atualizacao": datetime.now().isoformat(),
            "total_registros": len(todos_dados),
            "dados": todos_dados
        }
        
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"💾 JSON salvo em: {arquivo_json}")
        print(f"🎉 Concluído! Total de registros: {len(todos_dados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o scraping: {e}")
        import traceback
        traceback.print_exc()
        
        # Salvar log de erro
        os.makedirs('data', exist_ok=True)
        with open('data/error_log.txt', 'w', encoding='utf-8') as f:
            f.write(f"Erro em {datetime.now()}\n")
            f.write(str(e))
            f.write("\n\nTraceback:\n")
            f.write(traceback.format_exc())
            
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
