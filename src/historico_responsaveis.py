# src/historico_responsaveis.py
# -*- coding: utf-8 -*-
import os
import re
import json
import time
import random
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

# =============================
# Configurações do Coletor
# =============================
ORGAO_CODIGO = os.getenv("ORGAO_CODIGO", "32205")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))  # segundos
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# URLs alvo
URL_CONTRATOS_JSON_GERADO = "data/contratos.json"  # saída do contratos.py
URL_CONTRATOS_LISTA = f"https://contratos.comprasnet.gov.br/transparencia/contratos?orgao=[{ORGAO_CODIGO}]"
URL_CONTRATOS_AJAX = "https://contratos.comprasnet.gov.br/transparencia/contratos/search"
URL_CONTRATO_DETALHE = "https://contratos.comprasnet.gov.br/transparencia/contratos/{}"

# =============================
# Utilidades
# =============================
def norm(txt: str) -> str:
    if txt is None:
        return ""
    return re.sub(r"\s+", " ", str(txt)).strip().lower()

def sleep_jitter(base=REQUEST_DELAY):
    time.sleep(base + random.uniform(0, 0.4))

def today_date() -> date:
    return datetime.today().date()

def parse_iso_date(d: str):
    if not d:
        return None
    try:
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    except Exception:
        return None

# =============================
# Sessão HTTP + headers
# =============================
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    return s

def get_csrf_token(s: requests.Session) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = s.get(URL_CONTRATOS_LISTA, timeout=TIMEOUT)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            meta = soup.find("meta", {"name": "csrf-token"})
            if not meta or not meta.get("content"):
                raise RuntimeError("Meta csrf-token não encontrado")
            token = meta["content"]
            return token
        except Exception as e:
            if attempt >= MAX_RETRIES:
                raise
            sleep_jitter()
    return None

def buscar_id_contrato(s: requests.Session, csrf_token: str, numero_contrato: str):
    """
    Usa o endpoint AJAX para localizar o ID interno do contrato na tabela.
    """
    headers = {
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://contratos.comprasnet.gov.br",
        "Referer": URL_CONTRATOS_LISTA,
        "User-Agent": s.headers.get("User-Agent", "Mozilla/5.0"),
    }

    payload = {
        "draw": 1,
        "start": 0,
        "length": 10,
        "numerocontrato": numero_contrato,
        "orgao": f"[\"{ORGAO_CODIGO}\"]"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = s.post(URL_CONTRATOS_AJAX, data=payload, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            # varremos todas as células à procura do link /transparencia/contratos/{id}
            for linha in data:
                for celula in linha:
                    m = re.search(r'/transparencia/contratos/(\d+)', str(celula))
                    if m:
                        return m.group(1)
            return None
        except Exception:
            if attempt >= MAX_RETRIES:
                return None
            sleep_jitter()

def match_headers(actual_headers, expected_headers):
    """
    Compara listas de headers desprezando maiúsc/minúsc e espaços múltiplos.
    """
    a = [norm(h) for h in actual_headers]
    e = [norm(h) for h in expected_headers]
    return a == e

def extrair_historico(soup: BeautifulSoup):
    """
    Procura por tabela com headers:
    ["Data Assinatura", "Número", "Tipo", "Observação", "Data Início", "Data Fim", "Vlr. Global", "Parcelas", "Vlr. Parcela"]
    """
    alvo = ["Data Assinatura", "Número", "Tipo", "Observação", "Data Início", "Data Fim", "Vlr. Global", "Parcelas", "Vlr. Parcela"]
    resultado = []

    for tabela in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tabela.find_all("th")]
        if match_headers(headers, alvo):
            # linhas
            for tr in tabela.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) == 9:
                    resultado.append({
                        "data_assinatura": tds[0].get_text(strip=True),
                        "numero": tds[1].get_text(strip=True),
                        "tipo": tds[2].get_text(strip=True),
                        "observacao": tds[3].get_text(strip=True),
                        "data_inicio": tds[4].get_text(strip=True),
                        "data_fim": tds[5].get_text(strip=True),
                        "valor_global": tds[6].get_text(strip=True),
                        "parcelas": tds[7].get_text(strip=True),
                        "valor_parcela": tds[8].get_text(strip=True),
                    })
            break
    return resultado

def extrair_responsaveis(soup: BeautifulSoup):
    """
    Procura por tabela com headers: ["CPF", "Nome", "Tipo"]
    """
    alvo = ["CPF", "Nome", "Tipo"]
    resultado = []

    for tabela in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tabela.find_all("th")]
        if match_headers(headers, alvo):
            for tr in tabela.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) == 3:
                    resultado.append({
                        "cpf": tds[0].get_text(strip=True),
                        "nome": tds[1].get_text(strip=True),
                        "tipo": tds[2].get_text(strip=True),
                    })
            break
    return resultado

def carregar_contratos_base(caminho=URL_CONTRATOS_JSON_GERADO):
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo base não encontrado: {caminho}. "
            f"Certifique-se que o workflow de contratos gerou data/contratos.json antes."
        )
    with open(caminho, "r", encoding="utf-8") as f:
        base = json.load(f)
    dados = base.get("dados", [])
    return dados

def salvar_json(caminho, dados_array):
    os.makedirs("data", exist_ok=True)
    saida = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total_registros": len(dados_array),
        "dados": dados_array
    }
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

def main():
    print("🚀 Coletando Histórico e Responsáveis no Comprasnet...")
    contratos = carregar_contratos_base()

    # Filtra vigentes (ou sem data final)
    hoje = today_date()
    contratos_vigentes = []
    for c in contratos:
        vf = parse_iso_date(c.get("dataVigenciaFinal"))
        if vf is None or vf >= hoje:
            num = c.get("numeroContrato")
            if num:
                contratos_vigentes.append(num)

    # Evitar duplicados
    contratos_vigentes = sorted(set(contratos_vigentes))

    print(f"🧾 Contratos vigentes a processar: {len(contratos_vigentes)}")
    if not contratos_vigentes:
        # Mesmo assim gera arquivos vazios, para padronizar
        salvar_json("data/historico.json", [])
        salvar_json("data/responsaveis.json", [])
        print("✅ Nenhum contrato vigente. Arquivos vazios gerados.")
        return True
    s = make_session()
    print("🔑 Obtendo CSRF token...")
    csrf = get_csrf_token(s)
    print(f"✅ CSRF OK ({csrf[:10]}...)")

    historico_final = []
    responsaveis_final = []

    id_cache = {}  # cache numeroContrato -> id

    for i, numero in enumerate(contratos_vigentes, start=1):
        print(f"[{i}/{len(contratos_vigentes)}] 🔎 Buscando ID do contrato {numero}...")
        if numero in id_cache:
            contrato_id = id_cache[numero]
        else:
            contrato_id = buscar_id_contrato(s, csrf, numero)
            id_cache[numero] = contrato_id

        if not contrato_id:
            print(f"⚠️ ID interno não encontrado para {numero}")
            sleep_jitter()
            continue
        url_detalhe = URL_CONTRATO_DETALHE.format(contrato_id)
        print(f"📄 Baixando detalhes: {url_detalhe}")
        # GET com retry
        detalhe_html = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = s.get(url_detalhe, timeout=TIMEOUT)
                r.raise_for_status()
                detalhe_html = r.text
                break
            except Exception as e:
                print(f"   ❌ Falha ao carregar detalhes (tentativa {attempt}/{MAX_RETRIES}): {e}")
                if attempt >= MAX_RETRIES:
                    detalhe_html = None
                else:
                    sleep_jitter(REQUEST_DELAY + 0.5)

        if not detalhe_html:
            print(f"⚠️ Ignorando contrato {numero} (sem HTML).")
            continue

        soup = BeautifulSoup(detalhe_html, "html.parser")

        hist = extrair_historico(soup)
        resp = extrair_responsaveis(soup)

        historico_final.append({
            "numeroContrato": numero,
            "historico": hist
        })
        responsaveis_final.append({
            "numeroContrato": numero,
            "responsaveis": resp
        })

        sleep_jitter()

    # Salvar arquivos
    salvar_json("data/historico.json", historico_final)
    salvar_json("data/responsaveis.json", responsaveis_final)

    print("✅ Arquivos gerados com sucesso:")
    print(" - data/historico.json")
    print(" - data/responsaveis.json")
    return True

if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
