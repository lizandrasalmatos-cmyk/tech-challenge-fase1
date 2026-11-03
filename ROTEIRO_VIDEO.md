# Roteiro de demonstração - aproximadamente 6 a 8 minutos

Use como apoio para falar com suas palavras. Antes de gravar, execute o projeto e confira as métricas em `resultados/metricas_teste.csv`.

## 0:00 a 0:40 - Apresentação

Apresente seu nome, RM e o objetivo: comparar dois modelos que classificam amostras de tumores de mama como benignas ou malignas usando uma tabela de medidas celulares.

## 0:40 a 1:30 - Dados

Mostre `dados/base_cancer_mama.csv`. Explique que são 569 amostras, 30 variáveis numéricas e um alvo. O valor 1 significa maligno. Os dados vêm da UCI e são carregados pelo scikit-learn. Não são prontuários do hospital nem imagens processadas pelo projeto.

## 1:30 a 2:40 - Código

Abra `src/main.py` e mostre a divisão em treino, validação e teste. Explique: treino ensina o modelo, validação ajuda a escolher entre os modelos e teste mede o resultado final. Mostre os pipelines. A mediana trata ausências e a padronização deixa as escalas comparáveis na regressão logística. A árvore tem profundidade limitada.

## 2:40 a 3:40 - Executar

No terminal da pasta do projeto:

```powershell
.venv\Scripts\python.exe src/main.py
```

Espere terminar e mostre as métricas. Diga qual modelo foi escolhido na validação. Explique que o recall de malignos foi priorizado porque um falso negativo deixa de sinalizar uma amostra maligna.

## 3:40 a 5:10 - Resultados

Abra `resultados/distribuicoes.png`, `correlacao.png` e `matrizes_confusao.png`. Na matriz, as linhas são os valores reais e as colunas são os previstos. O quadrante maligno real e benigno previsto contém os falsos negativos. Use os números que aparecem nos seus resultados.

## 5:10 a 6:10 - Interpretação

Mostre `importancia_arvore.png`, `shap_arvore.png` e `coeficientes_logistica.png`. Explique que a importância mostra quais variáveis a árvore usou. SHAP descreve a contribuição das variáveis para as previsões da árvore. O gráfico usa a média das contribuições absolutas na validação e não mostra o sentido de cada contribuição. Coeficiente positivo na regressão favorece a classe maligno. Nenhuma dessas análises prova causalidade.

## 6:10 a 7:00 - Limitações e fechamento

Mostre o PDF e o README. Explique que a base é pequena e histórica, e que um bom resultado nesse teste não garante funcionamento em um hospital. Seriam necessários dados externos, avaliação clínica e cuidados com privacidade. O médico tem a decisão final. Mostre o Dockerfile e explique que o README contém os comandos para executar em contêiner; só afirme que executou Docker se realmente tiver feito isso.
