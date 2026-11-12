# %%
# importar pacotes necessários
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import unicodedata


# %%
#abrir arquivo csv
df = pd.read_csv("2026-11-08_156_-_Base_de_Dados.csv", sep = ";", encoding = "utf-8")

# %%
# Ver colunas do dataframe
df.columns

# %%
df.drop(columns=['Unnamed: 11'], inplace=True)

# %%
df.info()

# %% [markdown]
# Seleção de assunto especifico
# 

# %%
df['Assunto'].value_counts()

# %% [markdown]
# ##### Separando apenas pedidos envolvidos com Árvores

# %%
#selecionando apenas colunas de assunto "Árvore" para análise
df_arvores = df[df['Assunto'] == 'Árvore']

# %%
df_arvores["Subdivisao"].value_counts()

# %% [markdown]
# ##### Separando pedidos por data, sendo antes e após ventania dia 07/11/2026

# %%
# Separando dataset por data, antes do dia 07/11/2026 e depois do dia 07/11/2026
df_arvores['DataCriacao'] = pd.to_datetime(df_arvores['DataCriacao'], format='%d/%m/%Y')
df_arvores_antes = df_arvores[df_arvores['DataCriacao'] < pd.to_datetime('07/11/2026', format='%d/%m/%Y')]
df_arvores_depois = df_arvores[df_arvores['DataCriacao'] >= pd.to_datetime('07/11/2026', format='%d/%m/%Y')]

# Filtrando apenas os pedidos de Árvore ou galho caído – com bloqueio de passagem  e Árvore ou galho caído – sem bloqueio de passagem   
df_arvores_depois = df_arvores_depois[df_arvores_depois["Subdivisao"].isin(["Árvore ou galho caído – com bloqueio de passagem", "Árvore ou galho caído – sem bloqueio de passagem"])]

#Salvando o dataframe em csv depois do dia 07/11/2026
df_arvores_depois.to_csv('df_arvores_depois.csv', index=False, sep=';', encoding='utf-8')


# Filtrando apenas os pedidos de poda que estão abertos
df_arvores_antes = df_arvores_antes[df_arvores_antes["Situacao"] == "Aberto"]

#Selecionando apenas arvores abertas com as Subdivisões "Poda de manutenção em árvores" e "Avaliação para corte em via pública" 
df_arvores_antes = df_arvores_antes[df_arvores_antes["Subdivisao"].isin(["Poda de manutenção em árvores", "Avaliação para corte em via pública"])]

#salvando o dataframe em csv antes do dia 07/11/2026
df_arvores_antes.to_csv('df_arvores_antes_aberto.csv', index=False, sep=';', encoding='utf-8')



# %%
# Plotar gráfico de barras para visualizar a quantidade de pedidos de poda antes do dia 07/11/2026
plt.figure(figsize=(10, 6))
df_arvores_antes['Subdivisao'].value_counts().plot(kind='bar')
plt.xlabel('Subdivisão')    
plt.ylabel('Quantidade')
plt.title('Quantidade de Pedidos de Poda e Quedas de Árvores')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#plotar gráfico de barras para visualizar a quantidade de pedidos de queda de árvores depois do dia 07/11/2026
plt.figure(figsize=(10, 6))
df_arvores_depois['Subdivisao'].value_counts().plot(kind='bar')
plt.xlabel('Subdivisão')
plt.ylabel('Quantidade')
plt.title('Quantidade de Pedidos de Quedas de Árvores')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()




# %% [markdown]
# #### Limpeza de lougradouro para possibilitar avaliação de sobreposição

# %%

# 1. Carregar as bases que você salvou anteriormente
df_antes = pd.read_csv('df_arvores_antes_aberto.csv', sep=';', encoding='utf-8')
df_depois = pd.read_csv('df_arvores_depois.csv', sep=';', encoding='utf-8')

# 2. Criar uma coluna sinalizadora para facilitar a separação futura
df_antes['grupo_analise'] = 'antes_poda'
df_depois['grupo_analise'] = 'depois_queda'

# 3. Concatenar os datasets
df_arvores = pd.concat([df_antes, df_depois], ignore_index=True)

# 4. Função ajustada de limpeza do Logradouro (Sem extração de número e com remoção de acentos)
def limpar_logradouro(endereco):
    if pd.isna(endereco):
        return ""
    
    # Maiúsculas e remoção de acentos
    rua = str(endereco).upper().strip()
    rua = ''.join(c for c in unicodedata.normalize('NFD', rua) if unicodedata.category(c) != 'Mn')
    
    # Remover prefixos comuns de Curitiba
    prefixos = [r'^RUA\s+', r'^R\s+', r'^AVENIDA\s+', r'^AV\s+', r'^TRAVESSA\s+', r'^TR\s+', r'^PRACA\s+', r'^PC\s+', r'^ALAMEDA\s+', r'^AL\s+']
    for prefixo in prefixos:
        rua = re.sub(prefixo, '', rua)
        
    # Limpar pontuações residuais substituindo por espaço
    rua = re.sub(r'[.,;-]', ' ', rua)
    
    # Remover espaços duplos acidentais
    rua = re.sub(r'\s+', ' ', rua).strip()
    
    return rua

# 5. Aplicar a função diretamente na coluna Logradouro
df_arvores['Logradouro_Limpo'] = df_arvores['Logradouro'].apply(limpar_logradouro)

# Visualizar o resultado da limpeza
display(df_arvores[['Logradouro', 'Logradouro_Limpo', 'Bairro', 'grupo_analise']].head(10))
