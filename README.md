##🏢 **Scraper de dados abertos da ANP**

Automação para coleta de dados de contratos e faturas da ANP do portal de transparência.

## ⚙️ Funcionalidades
- 📋 Coleta automática de **faturas** via web scraping do portal de transparência
- 📄 Coleta de **contratos** através da API oficial de dados abertos
- 💾 Armazenamento em JSON estruturado e padronizado
- ⏰ Execução automática via GitHub Actions (segunda a sexta-feira)
- 🔄 Atualização diária dos dados

## 📊 Estrutura de Dados

Os dados são salvos em `data/*.json` com schema padronizado: ```json

{
  "ultima_atualizacao": "2024-01-15T10:30:00",
  "total_registros": 150,
  "dados": [...]
}

##🕐 Agendamento:

Faturas: Segunda a sexta, 5h UTC (2h BRT)

Contratos: Segunda a sexta, 6h UTC (3h BRT)


##📦 Dados Disponíveis:

Faturas: https://raw.githubusercontent.com/dadosabertosanp/scraper/main/data/faturas.json

Contratos: https://raw.githubusercontent.com/dadosabertosanp/scraper/main/data/contratos.json


##🚀 Como Usar:

Acesse os JSONs diretamente pelos links acima

Consuma no Power Apps, Excel, ou qualquer aplicação

Dados atualizados automaticamente diariamente


##🔐 Transparência e Segurança:

✅ Repositório público e aberto

✅ Apenas dados públicos oficiais

✅ Nenhuma credencial ou dado sensível

✅ Código aberto para auditoria


##🔗 Fontes Oficiais:

Portal de Transparência: https://contratos.comprasnet.gov.br

Faturas da ANP: https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=[32205]

API de Contratos: https://dadosabertos.compras.gov.br/modulo-contratos


##📈 Estatísticas de Execução:

⏱️ Tempo médio: 1-2 minutos por execução

📊 Consumo: ≈2% do limite gratuito mensal

💰 Custo: $0.00 (plano gratuito)


##💡 Informações Técnicas:

Desenvolvido em Python 3.10

Agendamento via GitHub Actions

JSON otimizado para Power Apps


