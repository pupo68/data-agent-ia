# app/agente_analista.py

import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
import uuid # Para gerar nomes de arquivo únicos

# --- 1. Imports e Configuração Inicial ---

# Encontra o caminho absoluto para o nosso arquivo de dados
# Isso garante que o script funcione, não importa de onde ele seja executado
try:
    DATA_FILE_PATH = Path(__file__).parent.parent.joinpath("data", "dados_financeiros.csv")
    df = pd.read_csv(DATA_FILE_PATH)
except FileNotFoundError:
    print("Erro: O arquivo 'dados_financeiros.csv' não foi encontrado.")
    print(f"Caminho procurado: {DATA_FILE_PATH}")
    # Cria um DataFrame vazio para que o resto do programa não quebre na importação
    df = pd.DataFrame()


# --- 2. Ferramentas do Agente ---

def analisar_dados_com_pandas(code_str: str) -> str:
    """
    Executa uma string de código Python/Pandas para analisar os dados financeiros.

    Use esta ferramenta para responder perguntas sobre os dados.
    O DataFrame está disponível como a variável `df`.

    O DataFrame `df` tem as seguintes colunas:
    - 'Data': Data da transação (ex: '2024-06-01')
    - 'Descricao': Descrição da transação (ex: 'Salario Mensal')
    - 'Categoria': Categoria da transação (ex: 'Salario', 'Moradia')
    - 'Valor': O valor numérico da transação.
    - 'Tipo': 'Receita' ou 'Despesa'.

    Exemplo de código: `df['Valor'].sum()` para obter a soma de todos os valores.
    Retorna o resultado da execução do código como uma string.
    """
    try:
        # Importante: O `eval` executa o código. Usamos `locals()` para dar acesso à variável `df`.
        # Usamos `str()` para garantir que a saída seja sempre uma string.
        output = str(eval(code_str, {"pd": pd, "df": df}))
        return output
    except Exception as e:
        # Retorna uma mensagem de erro clara se o código gerado pelo LLM falhar
        return f"Erro ao executar o código: {e}"


def gerar_grafico(x_column: str, y_column: str, title: str, chart_type: str = 'bar') -> str:
    """
    Gera um gráfico a partir dos dados e o salva como um arquivo de imagem.

    Use esta ferramenta quando o usuário pedir explicitamente por uma visualização ou gráfico.
    Retorna o caminho do arquivo de imagem salvo.

    :param x_column: O nome da coluna para o eixo X.
    :param y_column: O nome da coluna para o eixo Y.
    :param title: O título do gráfico.
    :param chart_type: O tipo de gráfico. Suportado: 'bar' (barras) ou 'pie' (pizza).
    """
    output_dir = Path(__file__).parent.parent.joinpath("graphics")
    # Cria a pasta /graphics/ se ela não existir
    output_dir.mkdir(exist_ok=True)
    
    # Gera um nome de arquivo único para não sobrescrever gráficos antigos
    filename = f"chart_{uuid.uuid4().hex[:6]}.png"
    filepath = output_dir.joinpath(filename)
    
    plt.figure(figsize=(10, 6))

    if chart_type == 'bar':
        plt.bar(df[x_column], df[y_column])
        plt.xlabel(x_column)
        plt.ylabel(y_column)
    elif chart_type == 'pie':
        # Para gráficos de pizza, faz mais sentido agrupar por categoria
        # Esta é uma lógica simples; o LLM pode fazer agregações mais complexas usando a outra ferramenta.
        data_agg = df.groupby(x_column)[y_column].sum()
        plt.pie(data_agg, labels=data_agg.index, autopct='%1.1f%%', startangle=140)
        plt.ylabel('') # Remove o label do eixo Y para pizza
    else:
        return f"Erro: Tipo de gráfico '{chart_type}' não suportado. Use 'bar' ou 'pie'."

    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close() # Libera a memória da figura
    
    return f"Gráfico gerado e salvo em: {filepath}"

# app/agente_analista.py (continuação)

# --- 3. Configuração do Agente Agno ---

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import GoogleChat

# Carrega as variáveis de ambiente (sua chave de API do Google)
load_dotenv()

# Lista de ferramentas que nosso agente poderá usar
tools = [
    analisar_dados_com_pandas,
    gerar_grafico
]

# Instruções detalhadas para o agente. Esta é a parte mais importante para o comportamento dele.
instructions = [
    "Você é um Analista de Dados Financeiros especialista.",
    "Sua função é ajudar os usuários a analisar um DataFrame do pandas chamado `df`.",
    "Para responder a perguntas, você DEVE usar a ferramenta `analisar_dados_com_pandas` gerando o código pandas apropriado.",
    "NUNCA responda com base em conhecimento geral. Sua resposta DEVE ser o resultado da execução da ferramenta.",
    "Se o usuário pedir um gráfico, use a ferramenta `gerar_grafico`.",
    "Se o código que você gerar resultar em um erro, analise o erro e tente gerar um código corrigido.",
    "Seja claro e direto na sua resposta final para o usuário.",
    "Ao apresentar resultados numéricos, como somas ou médias, formate-os de forma clara (ex: 'O total de receitas foi de R$ 15.000,00')."
]

# Criação do agente
data_analyst_agent = Agent(
    model=GoogleChat(model="gemini-pro"),
    tools=tools,
    instructions=instructions,
    # Habilitar o modo de depuração é ótimo durante o desenvolvimento para ver o que o agente está pensando
    debug_mode=True
)

# --- 4. Ponto de Entrada para Execução Interativa ---

if __name__ == "__main__":
    print("Agente Analista de Dados pronto! Faça suas perguntas.")
    data_analyst_agent.cli_chat()