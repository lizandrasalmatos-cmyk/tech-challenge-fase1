"""Experimento acadêmico: classificação de tumores com dados tabulares.

Execute da raiz: python src/main.py
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.datasets import load_breast_cancer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, recall_score, f1_score,
                             precision_score, confusion_matrix, ConfusionMatrixDisplay)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

OUT = ROOT / "resultados"
SEED = 42


def salvar_figura(nome):
    plt.tight_layout()
    plt.savefig(OUT / nome, dpi=150, bbox_inches="tight")
    plt.close()


def metricas(y, pred):
    # Classe positiva: maligno. Assim recall mede os malignos identificados.
    return {"accuracy": accuracy_score(y, pred),
            "recall": recall_score(y, pred, zero_division=0),
            "f1": f1_score(y, pred, zero_division=0),
            "precision": precision_score(y, pred, zero_division=0)}


def main():
    OUT.mkdir(exist_ok=True)
    (ROOT / "dados").mkdir(exist_ok=True)
    base = load_breast_cancer(as_frame=True)
    X = base.data.copy()
    # Na base original maligno=0. Aqui maligno=1 e benigno=0.
    y = (base.target == 0).astype(int).rename("maligno")
    dados = X.join(y)
    dados.to_csv(ROOT / "dados/base_cancer_mama.csv", index=False)
    ausentes = int(X.isna().sum().sum())
    duplicados = int(dados.duplicated().sum())
    infinitos = int(np.isinf(X.to_numpy()).sum())
    negativos = int((X < 0).sum().sum())
    # As medidas são não negativas. Entradas infinitas/negativas viram ausentes.
    X = X.replace([np.inf, -np.inf], np.nan).mask(X < 0)
    manter = ~dados.duplicated()
    X, y = X.loc[manter], y.loc[manter]

    # 60% treino, 20% validação e 20% teste; nenhuma linha se repete.
    X_dev, X_test, y_dev, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=SEED)
    X_train, X_val, y_train, y_val = train_test_split(
        X_dev, y_dev, test_size=0.25, stratify=y_dev, random_state=SEED)
    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)
    assert len(X_train) + len(X_val) + len(X_test) == len(X)
    partes = {"treino": y_train, "validacao": y_val, "teste": y_test}
    divisao = {nome: {"total": len(alvo), "malignos": int(alvo.sum()),
                     "benignos": int((alvo == 0).sum())}
               for nome, alvo in partes.items()}
    pd.DataFrame([{"linha": int(i), "conjunto": nome}
                  for nome, alvo in partes.items() for i in alvo.index]).to_csv(
                      OUT / "divisao_dados.csv", index=False)

    # A exploração usa somente treino para preservar o teste final.
    X_train.describe().T.to_csv(OUT / "estatisticas_treino.csv")
    y_train.value_counts().reindex([0, 1]).plot.bar(
        color=["#427c99", "#c96752"], rot=0, figsize=(6, 3))
    plt.xticks([0, 1], ["Benigno", "Maligno"])
    plt.ylabel("Quantidade")
    plt.title("Distribuição das classes no treino")
    salvar_figura("classes.png")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, coluna in zip(axes, ["mean radius", "mean texture"]):
        for valor, nome, cor in [(0, "Benigno", "#427c99"), (1, "Maligno", "#c96752")]:
            ax.hist(X_train.loc[y_train == valor, coluna], bins=18,
                    alpha=0.6, label=nome, color=cor)
        ax.set_title(coluna)
        ax.set_ylabel("Quantidade")
        ax.legend()
    salvar_figura("distribuicoes.png")
    corr = X_train.corr()
    corr.to_csv(OUT / "correlacao.csv")
    colunas = ["mean radius", "mean perimeter", "mean area", "mean texture",
               "mean concavity", "mean concave points"]
    fig, ax = plt.subplots(figsize=(7, 5))
    recorte = corr.loc[colunas, colunas]
    im = ax.imshow(recorte, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(6), colunas, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(6), colunas, fontsize=8)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{recorte.iloc[i,j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    ax.set_title("Correlação de Pearson no treino (recorte)")
    salvar_figura("correlacao.png")

    modelos = {
        "Regressão logística": Pipeline([
            ("imputacao", SimpleImputer(strategy="median")),
            ("escala", StandardScaler()),
            ("modelo", LogisticRegression(max_iter=2000, random_state=SEED))]),
        "Árvore de decisão": Pipeline([
            ("imputacao", SimpleImputer(strategy="median")),
            ("modelo", DecisionTreeClassifier(max_depth=4, min_samples_leaf=5,
                                             random_state=SEED))])}
    validacao = {}
    for nome, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        validacao[nome] = metricas(y_val, modelo.predict(X_val))
    # Critério definido antes de avaliar o teste: recall; desempate pelo F1.
    escolhido = max(validacao, key=lambda n: (validacao[n]["recall"], validacao[n]["f1"]))
    pd.DataFrame(validacao).T.to_csv(OUT / "metricas_validacao.csv")
    # Mantemos os modelos ajustados apenas no treino, sem reajuste no teste.
    teste = {}
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.7))
    matrizes = {}
    for ax, (nome, modelo) in zip(axes, modelos.items()):
        pred = modelo.predict(X_test)
        teste[nome] = metricas(y_test, pred)
        cm = confusion_matrix(y_test, pred, labels=[0, 1])
        matrizes[nome] = cm.tolist()
        ConfusionMatrixDisplay(cm, display_labels=["Benigno", "Maligno"]).plot(
            ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(nome)
        ax.set_xlabel("Previsto")
        ax.set_ylabel("Real")
    salvar_figura("matrizes_confusao.png")
    pd.DataFrame(teste).T.to_csv(OUT / "metricas_teste.csv")

    # Feature importance e SHAP da árvore; interpretação sem usar o teste.
    arvore = modelos["Árvore de decisão"]
    importancia = pd.Series(arvore.named_steps["modelo"].feature_importances_,
                            index=X.columns).sort_values(ascending=False)
    importancia.to_csv(OUT / "importancia_arvore.csv", header=["importancia"])
    importancia.head(8).sort_values().plot.barh(figsize=(7, 3.4), color="#427c99")
    plt.xlabel("Importância na árvore")
    plt.title("Variáveis usadas pela árvore")
    salvar_figura("importancia_arvore.png")
    val_transformado = arvore.named_steps["imputacao"].transform(X_val)
    explicador = shap.TreeExplainer(arvore.named_steps["modelo"])
    explicacao = explicador(val_transformado)
    # SHAP 0.49 retorna (amostras, variáveis, classes); classe 1 = maligno.
    valores = explicacao.values[:, :, 1]
    shap_medio = pd.Series(np.abs(valores).mean(axis=0), index=X.columns).sort_values(ascending=False)
    shap_medio.to_csv(OUT / "shap_arvore.csv", header=["shap_absoluto_medio"])
    shap_medio.head(8).sort_values().plot.barh(figsize=(7, 3.4), color="#c96752")
    plt.xlabel("Média do valor absoluto de SHAP (validação)")
    plt.title("Contribuição das variáveis na árvore - classe maligno")
    salvar_figura("shap_arvore.png")
    # Verifica se as contribuições recuperam a probabilidade prevista.
    reconstruido = explicacao.base_values[:, 1] + valores.sum(axis=1)
    assert np.allclose(reconstruido, arvore.predict_proba(X_val)[:, 1])
    # Coeficientes padronizados ajudam a interpretar a regressão logística.
    coef = pd.Series(modelos["Regressão logística"].named_steps["modelo"].coef_[0], index=X.columns)
    coef.to_csv(OUT / "coeficientes_logistica.csv", header=["coeficiente"])
    maiores_coef = coef.loc[coef.abs().sort_values(ascending=False).head(8).index]
    maiores_coef.sort_values().plot.barh(figsize=(7, 3.4), color="#427c99")
    plt.xlabel("Coeficiente após padronização")
    plt.title("Regressão logística: sinal positivo favorece maligno")
    salvar_figura("coeficientes_logistica.png")

    resumo = {"registros": len(X), "variaveis": X.shape[1], "ausentes": ausentes,
              "duplicados": duplicados, "infinitos": infinitos, "negativos": negativos,
              "divisao": divisao, "validacao": validacao, "teste": teste,
              "escolhido": escolhido, "matrizes": matrizes,
              "correlacao_raio_perimetro": float(corr.loc["mean radius", "mean perimeter"]),
              "importancia_top3": importancia.head(3).to_dict(),
              "shap_top3": shap_medio.head(3).to_dict(),
              "coeficientes_top3": maiores_coef.iloc[:3].to_dict(),
              "baseline_accuracy_teste": float((y_test == 0).mean())}
    (OUT / "resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nValidação:\n", pd.DataFrame(validacao).T.round(4).to_string())
    print("\nModelo escolhido na validação:", escolhido)
    print("\nTeste final:\n", pd.DataFrame(teste).T.round(4).to_string())
    print("\nMatriz [linhas reais, colunas previstas; ordem benigno, maligno]:")
    print(matrizes[escolhido])
    print("\nArquivos gerados em:", OUT)


if __name__ == "__main__":
    main()
