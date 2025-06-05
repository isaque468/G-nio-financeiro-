Prompt para o Bot Telegram: Gênio Financeiro

Nome do Bot: Gênio Financeiro (@GenioFinanceiro_bot)
Público-Alvo: Usuários que buscam gerenciar finanças pessoais de forma simples e interativa no Telegram.
Personalidade: Amigável, entusiasmada, com tom mágico e motivacional (ex.: "Que MASSSSSAA", "mapa do tesouro").
Identidade Visual: Gênio cartoon com turbante vibrante, roupa dourada, cercado por moedas e gráficos financeiros.

Funcionalidades Principais:
- Boas-Vindas (/start ou /recomecar): Pergunta o nome ("Qual seu nome, Mestre?") e personaliza saudações ("Bem-vindo(a) de volta, {Nome}! ✨"). Armazena nome.
- Registro de Renda: Solicita renda mensal e dias de pagamento ("Qual sua renda principal (apenas valor) e dia(s) de pagamento?"). Valida entrada numérica.
- Registro de Gastos: Permite registrar múltiplos gastos em uma mensagem (ex.: "Almoço 35, ração 120"). Extrai descrição e valor, armazena como dicionário.
- Resumo Financeiro (/resumo): Exibe renda, total de gastos, saldo e lista de gastos (ex.: "1. Almoço - R$35").
- Alterar Renda (/alterar_renda): Atualiza renda e dias de pagamento.
- Alterar Gasto (/alterar_gasto): Lista gastos, permite selecionar e editar um item.

Fluxos e Estados:
- Estados: idle, awaiting_name, awaiting_income_and_day, collecting_expenses, awaiting_income_correction, awaiting_expense_index_for_alteration.
- Respostas Negativas: "Não", "Parar" → "Ok, investidor {Nome}! Se precisar, diga 'Oi'." (volta ao estado idle).
- Retomada com "Oi": "Oi, {Nome}! Quais opções deseja? ✨".
- Mensagens Não Reconhecidas: "Não entendi, {Nome}. Use os botões ou diga 'Oi'." (reseta pra idle).
- Teclado: Botões /resumo, /alterar_renda, /alterar_gasto, /recomecar.

Persistência: Dados (nome, renda, gastos) salvos em context.user_data.
Deploy: Rodando automaticamente na Render.
Código: Disponível em https://github.com/isaque468/G-nio-financeiro-.
