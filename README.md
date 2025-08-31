# 🏢 Scraper de Faturas ANP

Automação para coleta de dados de faturas da ANP do portal de transparência.

## ⚙️ Funcionalidades

- Coleta automática diária de faturas
- Armazenamento em JSON estruturado
- Execução via GitHub Actions

## 📊 Estrutura de Dados

Os dados são salvos em `data/faturas_anp.json` com:
- Data da última atualização
- Total de registros
- Array com todos os registros

## 🚀 Como Usar

1. O scraper executa automaticamente todo dia às 5h (BRT)
2. Execute manualmente pela aba "Actions" no GitHub
3. Os dados ficam disponíveis em `data/faturas_anp.json`

## 🔐 Segurança

- Repositório público
- Apenas dados públicos
- Nenhuma credencial armazenada

## 🔗 Links Úteis
- **Dados JSON:** `https://raw.githubusercontent.com/dadosabertosanp/anp-faturas-scraper/main/data/faturas_anp.json`
- **Fonte Oficial:** https://contratos.comprasnet.gov.br
- **Página com faturas:** https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=%5B%2232205%22%5D
