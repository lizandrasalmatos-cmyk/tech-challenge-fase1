# Tech Challenge - Fase 1

**Aluna:** Lizandra Salvador Matos | **RM:** rm378867  
**Curso:** FIAP - IA para Devs

## Objetivo

Comparar regressão logística e árvore de decisão para classificar tumores de mama como benignos ou malignos. É um protótipo acadêmico de apoio à análise; não realiza diagnóstico clínico nem substitui o médico.

## Dados

Base Breast Cancer Wisconsin (Diagnostic), da UCI, disponível no próprio scikit-learn. São 569 registros e 30 medidas numéricas de núcleos celulares extraídas de imagens de punção aspirativa. O programa não recebe imagens e não prevê a presença de outras doenças. A cópia tabular está em `dados/base_cancer_mama.csv` e é recriada pelo script, sem download adicional.

- Fonte original: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic
- Carregamento: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
- Licença da base: CC BY 4.0. Autores: Wolberg, W., Mangasarian, O. e Street, W. (1995). DOI: https://doi.org/10.24432/C5DW2B
- O alvo foi recodificado: **0 = benigno; 1 = maligno**.

## Execução local

É necessário Python 3.12. No terminal, abra esta pasta e execute:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src/main.py
.venv\Scripts\python.exe src/gerar_relatorio.py
```

No Linux/macOS, substitua `.venv\Scripts\python.exe` por `.venv/bin/python`.

O primeiro script imprime os resultados e gera gráficos, tabelas e `resultados/resumo.json`. O segundo gera `output/pdf/relatorio_tecnico.pdf` a partir desses resultados. Não é preciso cadastrar conta no Kaggle ou configurar chaves.

## Execução com Docker

Com Docker instalado e em execução:

```bash
docker build -t tech-challenge-fase1 .
docker run --name desafio-fase1 tech-challenge-fase1
docker cp desafio-fase1:/app/resultados ./resultados-docker
docker rm desafio-fase1
```

O contêiner executa o experimento e mostra as métricas no terminal. Para gerar e copiar o PDF atualizado:

```bash
docker run --name relatorio-fase1 tech-challenge-fase1 python src/gerar_relatorio.py
docker cp relatorio-fase1:/app/output/pdf/relatorio_tecnico.pdf ./relatorio_tecnico.pdf
docker rm relatorio-fase1
```

## Organização

- `src/main.py`: carga, limpeza, exploração, modelos e avaliação.
- `src/gerar_relatorio.py`: geração do relatório PDF.
- `dados/`: dataset e explicação das colunas.
- `resultados/`: estatísticas, correlações, métricas e gráficos reais da execução.
- `output/pdf/`: relatório técnico.
- `entrega.json`: identificação e links que aparecem no PDF.

## Decisões do experimento

A separação estratificada usa aproximadamente 60% para treino, 20% para validação e 20% para teste, com `random_state=42`. A exploração usa somente treino. Valores infinitos e medidas negativas são convertidos em ausentes; duplicatas exatas são removidas antes da divisão. Na base fornecida não foram encontrados esses problemas.

A imputação pela mediana está dentro do pipeline. Na regressão logística há também padronização. Esses passos são ajustados somente no treino. As 30 entradas já são numéricas; não há categorias de entrada para codificar. O diagnóstico é o alvo e não entra nas características.

A árvore limita a profundidade a 4 e exige 5 exemplos por folha para reduzir sobreajuste. Não há busca extensa de hiperparâmetros. O limiar de classificação é o padrão dos modelos, sem ajuste no teste.

O modelo é escolhido pelo maior recall de malignos na validação, com F1 como desempate. O teste é usado uma vez ao final para comparar os dois modelos já treinados; não é usado para escolher ou ajustar modelos. Não há retreinamento com a validação. Accuracy, recall, F1 e precisão são calculados para a classe positiva maligno.

A interpretação inclui importância das variáveis e SHAP para a árvore, além de coeficientes padronizados para a regressão. SHAP é calculado na validação. As correlações entre medidas limitam a interpretação isolada de cada variável; importância não prova causa.

## Entrega

- Repositório: https://github.com/lizandrasalmatos-cmyk/tech-challenge-fase1
- Vídeo de demonstração: https://youtu.be/1myDvkwGU7o
- Relatório: `output/pdf/relatorio_tecnico.pdf`.

Os links e a identificação ficam em `entrega.json`. Caso sejam alterados, execute `python src/gerar_relatorio.py` para atualizar o PDF.

## Resultados obtidos

O modelo escolhido na validação foi a regressão logística (recall de 0,9767). No teste final, com 114 amostras:

| Modelo | Accuracy | Recall de malignos | F1 | Precisão |
| --- | --- | --- | --- | --- |
| Regressão logística | 0,9737 | 0,9524 | 0,9639 | 0,9756 |
| Árvore de decisão | 0,9298 | 0,8810 | 0,9024 | 0,9250 |

A regressão logística teve 71 verdadeiros negativos, 40 verdadeiros positivos, 1 falso positivo e 2 falsos negativos. Um classificador que previsse sempre benigno teria accuracy de 0,6316 e recall zero para malignos. Os resultados completos e gráficos estão em `resultados/` e no relatório PDF.

Os scripts foram executados em Python 3.12. O Dockerfile foi fornecido para reprodução; a execução em Docker não foi validada neste ambiente.
