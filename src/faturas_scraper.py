import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

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
            "orgao", "ug", "fornecedor", "contrato", "fundamento_legal", 
            "objeto", "observacao", "numero_fatura", "data_emissao", 
            "data_recebimento", "data_vencimento", "data_pagamento", 
            "valor_original", "retencao", "glosa", "deducoes", "valor_final", 
            "processo", "data_referencia", "sub_rogacao", "indicio_sobrepreco", 
            "mes", "ano", "situacao", "data_ultima_atualizacao"
        ]

        # Função para limpar HTML e tratar vazios
        def limpar_html(texto):
            if texto is None:
                return ""
            texto_limpo = BeautifulSoup(texto, "html.parser").get_text(strip=True)
            return texto_limpo if texto_limpo != "" else None

        # Função para converter moeda para número com tratamento de vazios
        def converter_moeda(valor):
            if not valor or valor.strip() == '' or valor is None:
                return 0.0
            
            # Remove R$, pontos e converte vírgula para ponto
            valor_limpo = re.sub(r'[R$\s\.\(\)]', '', str(valor))
            valor_limpo = valor_limpo.replace(',', '.')
            
            # Verifica se é negativo (quando entre parênteses)
            if '(' in str(valor) and ')' in str(valor):
                valor_limpo = '-' + valor_limpo
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                return 0.0

        # Função para converter data para formato ISO com tratamento de vazios
        def converter_data(data_str):
            if not data_str or data_str.strip() == '' or data_str is None:
                return None
            
            try:
                # Tenta converter de DD/MM/YYYY para YYYY-MM-DD
                data_obj = datetime.strptime(data_str.strip(), '%d/%m/%Y')
                return data_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                return None

        # Função para padronizar situação com tratamento de vazios
        def padronizar_situacao(situacao):
            if not situacao or situacao.strip() == '' or situacao is None:
                return "Não Informada"
            
            situacao = situacao.lower().strip()
            mapeamento = {
                'apropriação em andamento': 'Em Andamento',
                'apropriação andamento': 'Em Andamento',
                'paga': 'Paga',
                'liquidada': 'Liquidada',
                'vencida': 'Vencida',
                'cancelada': 'Cancelada',
                'em apropriação': 'Em Andamento',
                'apropriada': 'Apropriada',
                'em liquidação': 'Em Liquidação'
            }
            
            for key, value in mapeamento.items():
                if key in situacao:
                    return value
            
            return situacao.title()

        # Função segura para obter valor do dicionário
        def obter_valor_seguro(dicionario, chave, valor_padrao=None):
            return dicionario.get(chave, valor_padrao) if dicionario else valor_padrao

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
                
                # 🔧 TRANSFORMAÇÕES PARA POWER APPS
                # Converter valores monetários (com tratamento de nulos)
                registro_dict['valor_original'] = converter_moeda(obter_valor_seguro(registro_dict, 'valor_original'))
                registro_dict['retencao'] = converter_moeda(obter_valor_seguro(registro_dict, 'retencao'))
                registro_dict['glosa'] = converter_moeda(obter_valor_seguro(registro_dict, 'glosa'))
                registro_dict['deducoes'] = converter_moeda(obter_valor_seguro(registro_dict, 'deducoes'))
                registro_dict['valor_final'] = converter_moeda(obter_valor_seguro(registro_dict, 'valor_final'))
                
                # Converter datas (com tratamento de nulos)
                registro_dict['data_emissao'] = converter_data(obter_valor_seguro(registro_dict, 'data_emissao'))
                registro_dict['data_recebimento'] = converter_data(obter_valor_seguro(registro_dict, 'data_recebimento'))
                registro_dict['data_vencimento'] = converter_data(obter_valor_seguro(registro_dict, 'data_vencimento'))
                registro_dict['data_pagamento'] = converter_data(obter_valor_seguro(registro_dict, 'data_pagamento'))
                registro_dict['data_referencia'] = converter_data(obter_valor_seguro(registro_dict, 'data_referencia'))
                registro_dict['data_ultima_atualizacao'] = converter_data(obter_valor_seguro(registro_dict, 'data_ultima_atualizacao'))
                
                # Padronizar situação (com tratamento de nulos)
                registro_dict['situacao'] = padronizar_situacao(obter_valor_seguro(registro_dict, 'situacao'))
                
                # Extrair CNPJ do fornecedor (se existir)
                fornecedor = obter_valor_seguro(registro_dict, 'fornecedor', '')
                cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', str(fornecedor)) if fornecedor else None
                registro_dict['cnpj_fornecedor'] = cnpj_match.group(1) if cnpj_match else None
                
                # Extrair nome do fornecedor (removendo CNPJ se existir)
                if fornecedor and cnpj_match:
                    registro_dict['nome_fornecedor'] = re.sub(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\s*-\s*', '', fornecedor).strip()
                else:
                    registro_dict['nome_fornecedor'] = fornecedor
                
                # Garantir que todos os campos existam, mesmo que vazios
                for campo in CABECALHO:
                    if campo not in registro_dict:
                        registro_dict[campo] = None
                
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
            json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)

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
