# Base de dados

O arquivo `base_cancer_mama.csv` é gerado por `src/main.py`, usando `load_breast_cancer` do scikit-learn. A base original é a Breast Cancer Wisconsin (Diagnostic), UCI.

Cada linha representa uma amostra. Há 30 medidas numéricas e a coluna alvo `maligno`: 0 para benigno e 1 para maligno. A versão do scikit-learn não inclui identificador de paciente entre as entradas.

As medidas descrevem raio, textura, perímetro, área, suavidade, compacidade, concavidade, pontos côncavos, simetria e dimensão fractal. Para cada característica há média (`mean`), erro padrão (`error`) e `worst` (média dos três maiores valores). Os nomes originais foram mantidos para facilitar a conferência.

Fonte: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic

Wolberg, W., Mangasarian, O. e Street, W. (1995). Breast Cancer Wisconsin (Diagnostic). UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5DW2B. Licença CC BY 4.0.
