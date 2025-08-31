import requests
import json
import os
from datetime import datetime, timedelta
import time

def main():
    print("🚀 Iniciando coleta de contratos ANP via API...")
    
    try:
        # Configurações da API
        BASE_URL = "https://dadosabertos.compras.gov.br/modulo-contratos/1_consultarContratos"
        todos_contratos = []
        
        # Parâmetros fixos
        params_base = {
            "codigoOrgao": "32205",
            "tamanhoPagina": 500
        }
        
        # Período de busca (2000 até ano atual)
        ano_atual = datetime.now().year
        ano_inicio = 2000
        
        print(f"📅 Buscando contratos de {ano_inicio} a {ano_atual}...")
        
        # Loop por anos
        for ano in range(ano_inicio, ano_atual + 1):
            print(f"\n🔍 Processando ano {ano}...")
            
            data_inicio = f"{ano}-01-01"
            data_fim = f"{ano}-12-31"
            
            pagina = 1
            tem_mais_paginas = True
            
            while tem_mais_paginas:
                # Parâmetros da requisição
                params = params_base.copy()
                params.update({
                    "dataVigenciaInicialMin": data_inicio,
                    "dataVigenciaInicialMax": data_fim,
                    "pagina": pagina
                })
                
                print(f"   📄 Página {pagina}...")
                
                try:
                    # Fazer requisição
                    response = requests.get(BASE_URL, params=params, timeout=60)
                    response.raise_for_status()
                    
                    dados = response.json()
                    
                    # Extrair contratos
                    contratos = dados.get("resultado", [])
                    total_paginas = dados.get("totalPaginas", 1)
                    total_registros = dados.get("totalRegistros", 0)
                    
                    print(f"   ✅ {len(contratos)} contratos encontrados (Total: {total_registros})")
                    
                    if not contratos:
                        break
                    
                    # Processar e formatar cada contrato (mantendo TUDO)
                    for contrato in contratos:
                        contrato_formatado = formatar_contrato_completo(contrato)
                        todos_contratos.append(contrato_formatado)
                    
                    # Verificar se há mais páginas
                    if pagina >= total_paginas:
                        tem_mais_paginas = False
                    else:
                        pagina += 1
                    
                    # Delay para não sobrecarregar a API
                    time.sleep(0.5)
                        
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Erro na página {pagina}: {e}")
                    break
                except json.JSONDecodeError as e:
                    print(f"   ❌ Erro ao decodificar JSON: {e}")
                    break
        
        # Salvar dados
        salvar_contratos(todos_contratos)
        
        print(f"\n🎉 Concluído! Total de contratos coletados: {len(todos_contratos)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def formatar_contrato_completo(contrato):
    """Mantém todos os campos da API, apenas formatando valores"""
    return {
        # Identificação
        "codigoOrgao": contrato.get("codigoOrgao"),
        "nomeOrgao": contrato.get("nomeOrgao"),
        "codigoUnidadeGestora": contrato.get("codigoUnidadeGestora"),
        "nomeUnidadeGestora": contrato.get("nomeUnidadeGestora"),
        "codigoUnidadeGestoraOrigemContrato": contrato.get("codigoUnidadeGestoraOrigemContrato"),
        "nomeUnidadeGestoraOrigemContrato": contrato.get("nomeUnidadeGestoraOrigemContrato"),
        "receitaDespesa": contrato.get("receitaDespesa"),
        
        # Contrato
        "numeroContrato": contrato.get("numeroContrato"),
        "codigoUnidadeRealizadoraCompra": contrato.get("codigoUnidadeRealizadoraCompra"),
        "nomeUnidadeRealizadoraCompra": contrato.get("nomeUnidadeRealizadoraCompra"),
        "numeroCompra": contrato.get("numeroCompra"),
        
        # Modalidade
        "codigoModalidadeCompra": contrato.get("codigoModalidadeCompra"),
        "nomeModalidadeCompra": contrato.get("nomeModalidadeCompra"),
        "codigoTipo": contrato.get("codigoTipo"),
        "nomeTipo": contrato.get("nomeTipo"),
        
        # Categoria
        "codigoCategoria": contrato.get("codigoCategoria"),
        "nomeCategoria": contrato.get("nomeCategoria"),
        "codigoSubcategoria": contrato.get("codigoSubcategoria"),
        "nomeSubcategoria": contrato.get("nomeSubcategoria"),
        
        # Fornecedor
        "niFornecedor": contrato.get("niFornecedor"),
        "nomeRazaoSocialFornecedor": contrato.get("nomeRazaoSocialFornecedor"),
        
        # Detalhes
        "processo": contrato.get("processo"),
        "objeto": contrato.get("objeto"),
        "informacoesComplementares": contrato.get("informacoesComplementares"),
        
        # Datas (formatadas)
        "dataVigenciaInicial": formatar_data(contrato.get("dataVigenciaInicial")),
        "dataVigenciaFinal": formatar_data(contrato.get("dataVigenciaFinal")),
        "dataHoraInclusao": formatar_data_hora(contrato.get("dataHoraInclusao")),
        "dataHoraExclusao": formatar_data_hora(contrato.get("dataHoraExclusao")),
        
        # Valores (convertidos para número)
        "valorGlobal": float(contrato.get("valorGlobal", 0)) if contrato.get("valorGlobal") is not None else 0.0,
        "numeroParcelas": int(contrato.get("numeroParcelas", 0)) if contrato.get("numeroParcelas") is not None else 0,
        "valorParcela": float(contrato.get("valorParcela", 0)) if contrato.get("valorParcela") is not None else 0.0,
        "valorAcumulado": float(contrato.get("valorAcumulado", 0)) if contrato.get("valorAcumulado") is not None else 0.0,
        "totalDespesasAcessorias": float(contrato.get("totalDespesasAcessorias", 0)) if contrato.get("totalDespesasAcessorias") is not None else 0.0,
        
        # Controle
        "numeroControlePncpContrato": contrato.get("numeroControlePncpContrato"),
        "idCompra": contrato.get("idCompra"),
        "contratoExcluido": bool(contrato.get("contratoExcluido", False)),
        "unidadesRequisitantes": contrato.get("unidadesRequisitantes"),
        
        # Metadados
        "anoVigencia": extrair_ano(contrato.get("dataVigenciaInicial")),
        "dataColeta": datetime.now().isoformat()
    }

def formatar_data(data_str):
    """Converte data para formato ISO (apenas data)"""
    if not data_str:
        return None
    
    try:
        if "T" in data_str:
            return data_str.split("T")[0]
        return data_str
    except:
        return None

def formatar_data_hora(data_str):
    """Mantém datetime completo quando disponível"""
    return data_str if data_str else None

def extrair_ano(data_str):
    """Extrai ano da data"""
    if not data_str:
        return None
    
    try:
        if "T" in data_str:
            return int(data_str.split("T")[0].split("-")[0])
        return int(data_str.split("-")[0])
    except:
        return None

def salvar_contratos(contratos):
    """Salva os contratos em JSON"""
    os.makedirs('data', exist_ok=True)
    
    resultado = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total_registros": len(contratos),
        "dados": contratos
    }
    
    with open('data/contratos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"💾 Dados salvos em: data/contratos.json")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
