# 🏢 Scraper de dados abertos da ANP

Automação para coleta de dados de contratos e faturas da ANP do portal de transparência.

## ⚙️ Funcionalidades

- Coleta automática diária de faturas através de HTTP POST nas páginas.
- Coleta da API com contratos
- Armazenamento em JSON estruturado
- Execução via GitHub Actions agendado diariamente

## 📊 Estrutura de Dados

Os dados são salvos em `data/*******.json` com:
- Data da última atualização
- Total de registros
- Array com todos os registros

## 🚀 Como Usar

1. O scraper executa automaticamente todo dia às 5h (BRT)
2. Execute manualmente pela aba "Actions" no GitHub
3. Os dados ficam disponíveis em `data/*******.json`

## 🔐 Segurança

- Repositório público
- Apenas dados públicos
- Nenhuma credencial armazenada

## 🔗 Links Úteis
- **Fonte Oficial:** https://contratos.comprasnet.gov.br
- **Página com faturas:** https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=%5B%2232205%22%5D
- **URL das faturas em JSON:** "https://raw.githubusercontent.com/dadosabertosanp/scraper/main/data/faturas.json"
- **URL dos contratos em JSON:** "https://raw.githubusercontent.com/dadosabertosanp/scraper/main/data/contratos.json"




