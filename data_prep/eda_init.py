"""Evaluate the variables of a dataset in terms of statistical measures (minimum, maximum, mean, median, std, quantiles, kurtosis, skewness, ...) and kernel density estimation (KDE).
Present the types of the variables (integer, float, categorical, ...);
Use visualization tools to show histograms, pairplot, among others related to the variables of the choice dataset."""
#%%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder ### transformar variaveis categoricas em numericas

### modificar o caminho do arquivo
file_path = "C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/batch/test_city_40000_init_pop_100_years_1950_start_year_2024_03_15_batch_merged.csv"
data = pd.read_csv(file_path,low_memory=False)

def skewness_stat(df):
    df["skew_status"] = df["skew"].apply(lambda x: "direita" if x > 0.1 else "esq." if x < -0.1 else "simetrica")
    return df

def kurtosis_stat(df):
    df["kurtosis_status"] = df["kurtosis"].apply(lambda x: "pontiaguda" if x > 3 else "achatada" if x < 3 else "normal")
    return df

def get_skew_kurt(df):

    # skewness (assimetria): mede a assimetria da distribuicao
    ### se skew > 0.1 (), a distribuicao e assimetrica a direita
    # Isso significa que há uma concentração maior de valores no lado esq. da média,
    ### mas os valores extremos estão no lado direiro (cauda).
    ### Se skew < -0.1, a distribuicao e assimetrica a esquerda
    # Isso significa que há uma concentração maior de valores no lado dir. da média

    skew = df.skew().reset_index().rename(columns={"index":"variable",0:"skew"})

    ### kurtosis (curtose): mede a forma da distribuicao
    ### se kurt > 3, a distribuicao e leptocurtica (pico mais alto e caudas mais pesadas) (pontiaguda)
    ### se kurt < 3, a distribuicao e platicurtica (pico mais baixo e caudas mais leves) (achatada)
    ### se kurt = 3, a distribuicao e mesocurtica (similar a distribuicao normal)

    kurt = df.kurtosis().reset_index().rename(columns={"index":"variable",0:"kurtosis"})

    skew_kurt = skew.merge(kurt, on="variable")
    skew_kurt = skewness_stat(skew_kurt)
    skew_kurt = kurtosis_stat(skew_kurt)
    return skew_kurt

def plot_hist(data, var_plot, skew_kurt,kde=False):
    sns.histplot(data[var_plot], kde=kde)
    sns.lineplot(x=[data[var_plot].mean()]*2, 
                 y=[0, data[var_plot].count()], color="red")
    msk = skew_kurt['variable'] == var_plot
    skew = skew_kurt.loc[msk,'skew_status'].values[0]
    kurt = skew_kurt.loc[msk,'kurtosis_status'].values[0]
    skew_val = skew_kurt.loc[msk,'skew'].values[0]
    kurt_val = skew_kurt.loc[msk,'kurtosis'].values[0]

    text = f"distribuicao de {var_plot} - "
    text2 = f"{var_plot}\nskew: {skew} ({round(skew_val,2)})\nkurtosis: {kurt} ({round(kurt_val,2)})"
    plt.title(text + text2)
    plt.show()

### Extrair tamanho do dataset e tipos de variáveis
display(data.info())

### Remover colunas que estao vazias
data = data.dropna(axis=1, how='all')

### remover event Created
msk = data["event"] == "Created"
data = data[~msk]

### remover eventos em que o Income é nulo ou negativo
msk2 = (data["income"] <= 0) | (data["income"].isnull())
data = data[~msk2]

### Remover colunas com informacao pessoal ou que nao sao relevantes para a analise
cols_to_drop = ["first_name", "last_name","full_name",
                "age_range","future_career","years_to_study",
                "time_stamp","has_a_car","children_name_id","unique_name_year_event_id"]

data = data.drop(cols_to_drop, axis=1)

### Estatísticas descritivas das variáveis numéricas
display(round(data.describe().T,2))

### Como os dados sao eventos temporais e 
### cada linha representa uma "fotografia" da situacao de um individuo em um dado momento,
### os valores medios das variaveis nao sao muito informativos.
### para obter informacoes mais uteis, vamos selecionar um ano e calcular as estatisticas descritivas

msk3 = data["year"] == 1951
data_1951 = data[msk3]

display(round(data_1951.describe().T,2))

### Remover colunas com dados cujos os valores sao sempre os mesmos
cols_to_drop = ["married","just_married","children"]
data_1951 = data_1951.drop(cols_to_drop, axis=1)

skew_kurt = get_skew_kurt(data_1951)

display(skew_kurt)
#%%
var_plot = "years_of_study"
plot_hist(data_1951, var_plot, skew_kurt, kde=True)

var_plot = "age"
plot_hist(data_1951, var_plot, skew_kurt, kde=True)

var_plot = "income"
plot_hist(data_1951, var_plot, skew_kurt, kde=True)
#%%
### agrupar income em faixas - de cada 10000
custom_bins = range(-20000, 200000, 10000)

data_1951["income_group"] = pd.cut(data_1951["income"], bins = custom_bins)

### transformar em string e depois pegar o primeiro valor
data_1951["income_group"] = data_1951["income_group"].astype(str).str.split(",").str[0].str.split("(").str[1]
data_1951["income_group"] = data_1951["income_group"].astype(int)

### atualizar skew e kurt para income_group
skew_kurt = get_skew_kurt(data_1951)
display(skew_kurt)
#%%
### plotar histograma de income_group
var_plot = "income_group"
plot_hist(data_1951, var_plot, skew_kurt, kde=True)
### a transformacao em faixas de renda nao alterou a assimetria e a curtose da distribuicao

#%% correlograma - pairplot
msk = data_1951.dtypes == "float64"
num_vars = data_1951.columns[msk]

sns.pairplot(data_1951[num_vars])
plt.show()
#%%
### matriz de correlacao
corr = data_1951[num_vars].corr()

sns.heatmap(corr, annot=True)
plt.show()

### loan esta fortemente correlacionado com years_of_study e loan_term
### o que faz sentido, pois quanto mais anos de estudo, maior a chance de ter um emprestimo de maior valor
### income esta fortemente correlacionado com years_of_study
### interest_rate tem pouca correlacao com as outras variaveis
### income possui uma leve correlacao com balance pois quanto maior a renda, maior a chance de ter um saldo maior
#%%
### plote um grafico de dispersao entre income e balance
sns.scatterplot(x="income", y="balance", data=data_1951)
plt.show()

### o grafico mostra que a correlacao entre as variaveis income e balance nao e linear
### isso pode estar relacionado com a presenca de outra variavel que influencia a relacao entre as duas variaveis

### plotar grafico de dispersao entre income, balance e career
sns.scatterplot(x="income", y="balance", hue="career", data=data_1951)
plt.show()
### o grafico mostra que a variavel career pode influenciar a relacao entre income mas nao balance

### plotar grafico de dispersao entre income, balance e spender_prof
sns.scatterplot(x="income", y="balance", hue="spender_prof", data=data_1951)
plt.show()

### o ultimo grafico mostra que a variavel spender_prof pode influenciar a relacao entre income e balance
# %%
le = LabelEncoder()

cat_vars = data_1951.select_dtypes(include="object").columns
### remova event e unique_name_id
cat_vars = cat_vars.drop(["event","unique_name_id"])

for var in cat_vars:
    data_1951[var+"_enc"] = le.fit_transform(data_1951[var])

corr = round(data_1951.corr(),2)

sns.heatmap(corr, annot=True)

plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
plt.gcf().set_size_inches(10,10)

plt.show()

# %%
