"""Gera o PDF a partir dos resultados de main.py e dos dados de entrega.json."""
import json
import csv
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resultados"


def main():
    if not (OUT / "resumo.json").exists():
        raise SystemExit("Execute python src/main.py antes de gerar o relatório.")
    r = json.loads((OUT / "resumo.json").read_text(encoding="utf-8"))
    entrega = json.loads((ROOT / "entrega.json").read_text(encoding="utf-8"))
    destino = ROOT / "output/pdf/relatorio_tecnico.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name="Texto", fontName="Helvetica", fontSize=10.3,
                              leading=15, spaceAfter=9))
    estilos.add(ParagraphStyle(name="Pequeno", fontName="Helvetica", fontSize=8.5,
                              leading=12, spaceAfter=7))
    estilos.add(ParagraphStyle(name="Capa", fontName="Helvetica-Bold", fontSize=23,
                              leading=29, alignment=TA_CENTER, spaceAfter=20,
                              textColor=colors.HexColor("#234455")))
    estilos["Heading1"].textColor = colors.HexColor("#234455")
    estilos["Heading1"].fontSize = 17
    estilos["Heading1"].spaceAfter = 14
    story = []

    def p(texto, estilo="Texto"):
        story.append(Paragraph(texto, estilos[estilo]))

    def titulo(texto):
        p(texto, "Heading1")

    def imagem(nome, largura=16, altura=None):
        img = Image(str(OUT / nome))
        proporcao = img.imageHeight / img.imageWidth
        img.drawWidth = largura * cm
        img.drawHeight = largura * cm * proporcao
        if altura and img.drawHeight > altura * cm:
            img.drawHeight = altura * cm
            img.drawWidth = img.drawHeight / proporcao
        story.append(img)
        story.append(Spacer(1, 0.15 * cm))

    def tabela(linhas, larguras):
        celulas = [[Paragraph(escape(str(c)), estilos["Pequeno"]) for c in linha] for linha in linhas]
        t = Table(celulas, colWidths=[x * cm for x in larguras], repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7eef2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#78909c")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#dbe1e4")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    def pagina():
        story.append(PageBreak())

    def link_ou_pendente(chave, rotulo):
        valor = entrega.get(chave, "").strip()
        if valor.startswith(("https://", "http://")):
            p(f'<b>{rotulo}:</b> <link href="{escape(valor, {chr(34): "&quot;"})}" color="#245d80">{escape(valor)}</link>', "Pequeno")
        else:
            p(f"<b>{rotulo}:</b> pendente de publicação.", "Pequeno")

    story.append(Spacer(1, 2 * cm))
    p("FIAP", "Capa")
    p("Pós-graduação - IA para Devs", "Title")
    story.append(Spacer(1, 1 * cm))
    p("Tech Challenge<br/>Fase 1", "Capa")
    p("Classificação de tumores de mama<br/>com Machine Learning", "Title")
    story.append(Spacer(1, 1.5 * cm))
    p(escape(entrega["nome"]), "Title")
    p("RM: " + escape(entrega["rm"]), "Title")
    story.append(Spacer(1, 1.3 * cm))
    link_ou_pendente("repositorio", "Repositório Git")
    link_ou_pendente("video", "Vídeo de demonstração")
    story.append(Spacer(1, 0.7 * cm))
    p("2026", "Title")

    pagina()
    titulo("1. Problema e base de dados")
    p("O objetivo foi desenvolver uma solução inicial para classificar amostras de tumores de mama como benignas ou malignas. A proposta é apoiar a análise de exames por meio de dados estruturados, mantendo a decisão final com o médico.")
    p("Foi utilizada a base pública Breast Cancer Wisconsin (Diagnostic), da UCI, carregada pela biblioteca scikit-learn [1, 2]. Ela possui 569 amostras e 30 variáveis numéricas. As medidas foram extraídas de imagens de núcleos celulares obtidas por punção aspirativa de uma massa mamária. Neste projeto, foram utilizadas as medidas já organizadas em tabela.")
    p("As variáveis descrevem raio, textura, perímetro, área, suavidade, compacidade, concavidade, pontos côncavos, simetria e dimensão fractal. Para cada característica há média, erro padrão e uma medida dos maiores valores. Não existem variáveis categóricas de entrada nesta versão da base.")
    p("O diagnóstico foi recodificado para <b>0 = benigno</b> e <b>1 = maligno</b>. Assim, as métricas de recall, precisão e F1 se referem à detecção de malignos. O alvo não foi usado como entrada do modelo.")
    titulo("2. Exploração dos dados")
    d = r["divisao"]
    p(f"A base contém 357 amostras benignas e 212 malignas. A exploração foi realizada apenas no conjunto de treino, com {d['treino']['total']} amostras, preservando os dados de teste para a avaliação final. Foram calculadas média, desvio padrão, mínimo, quartis e máximo de cada variável. A tabela completa está em resultados/estatisticas_treino.csv.")
    imagem("classes.png", largura=12, altura=5.2)
    p("Há mais exemplos benignos que malignos. Por isso, a acurácia isolada pode esconder falhas na identificação da classe maligna. A divisão estratificada mantém proporções semelhantes nos três conjuntos.")
    with (OUT / "estatisticas_treino.csv").open(encoding="utf-8", newline="") as arquivo:
        estatisticas = {linha[""]: linha for linha in csv.DictReader(arquivo)}
    tabela([["Variável (treino)", "Média", "Desvio padrão", "Mínimo", "Máximo"]] + [
        [nome] + [f"{float(estatisticas[nome][k]):.2f}" for k in ["mean", "std", "min", "max"]]
        for nome in ["mean radius", "mean texture", "mean area"]], [5.4, 2.5, 3.1, 2.5, 2.5])
    p("As medidas têm escalas diferentes, especialmente a área em relação ao raio. Essa diferença motivou a padronização na regressão logística.")

    pagina()
    titulo("3. Distribuições e correlação")
    imagem("distribuicoes.png", largura=16, altura=6)
    p("O raio médio apresenta maior concentração em valores altos nas amostras malignas. A textura também apresenta diferenças, mas há sobreposição entre as classes. Uma medida isolada não separa todos os casos.")
    imagem("correlacao.png", largura=13.2, altura=8)
    p(f"O recorte da correlação de Pearson mostra medidas relacionadas. A correlação entre raio médio e perímetro médio foi {r['correlacao_raio_perimetro']:.3f}. Isso é esperado porque ambas descrevem tamanho. Todas as 30 variáveis foram mantidas nesta primeira versão; a matriz completa está em resultados/correlacao.csv.")
    p("A correlação elevada indica informação parcialmente repetida e exige cuidado ao interpretar a importância individual das variáveis. Não significa relação de causa e efeito.")

    pagina()
    titulo("4. Pré-processamento e modelagem")
    p(f"A verificação encontrou {r['ausentes']} valores ausentes, {r['duplicados']} linhas duplicadas, {r['infinitos']} valores infinitos e {r['negativos']} medidas negativas. O código converte infinitos e medidas negativas em ausentes e remove duplicatas exatas, caso apareçam. Não foram removidos valores extremos apenas por serem altos, pois podem representar amostras válidas.")
    p("Foi utilizado um pipeline de imputação pela mediana. Na regressão logística, também foi aplicado StandardScaler para padronizar as variáveis. Esses passos foram ajustados somente no treino, evitando usar informações da validação ou do teste. As entradas já são numéricas; apenas o alvo binário precisou ser recodificado.")
    linhas = [["Conjunto", "Total", "Benignos", "Malignos"]]
    for nome, valores in d.items():
        linhas.append([nome.capitalize(), valores["total"], valores["benignos"], valores["malignos"]])
    tabela(linhas, [5, 3, 4, 4])
    p("A separação foi aproximadamente 60% para treino, 20% para validação e 20% para teste, com estratificação e random_state=42. Os conjuntos não compartilham linhas. O arquivo divisao_dados.csv registra a divisão.")
    p("<b>Regressão logística:</b> escolhida como modelo inicial simples, com C=1 e limite de 2.000 iterações. A padronização reduz o efeito das diferenças de escala.")
    p("<b>Árvore de decisão:</b> escolhida por representar regras de separação e permitir analisar a importância das variáveis. Foram definidos profundidade máxima 4 e mínimo de 5 amostras por folha para limitar o sobreajuste.")
    p("Os dois modelos foram treinados apenas no treino. O critério de escolha foi o maior recall de malignos na validação, usando F1 como desempate. Os hiperparâmetros e o limiar padrão de classificação foram mantidos sem ajustes a partir do teste. Não foi feita busca extensa de parâmetros.")
    titulo("5. Resultado na validação")
    tabela([["Modelo", "Accuracy", "Recall", "F1"]] + [
        [nome] + [f"{m[k]:.4f}" for k in ["accuracy", "recall", "f1"]]
        for nome, m in r["validacao"].items()], [6.7, 3.1, 3.1, 3.1])
    p(f"O modelo escolhido foi <b>{r['escolhido'].lower()}</b>. Após essa escolha, os dois modelos foram avaliados no teste, sem novo treinamento ou mudança de parâmetros.")

    pagina()
    titulo("6. Avaliação no teste")
    tabela([["Modelo", "Accuracy", "Recall", "F1", "Precisão"]] + [
        [nome] + [f"{m[k]:.4f}" for k in ["accuracy", "recall", "f1", "precision"]]
        for nome, m in r["teste"].items()], [5.8, 2.55, 2.55, 2.55, 2.55])
    p("Accuracy é a proporção total de acertos. Recall mede a proporção de malignos identificados. Precisão mede quantas previsões de maligno estavam corretas. F1 resume o equilíbrio entre precisão e recall. O recall foi priorizado porque um falso negativo deixa de sinalizar uma amostra maligna, embora falsos positivos também possam gerar exames e preocupação desnecessários.")
    imagem("matrizes_confusao.png", largura=16, altura=7)
    nome = r["escolhido"]
    tn, fp = r["matrizes"][nome][0]
    fn, tp = r["matrizes"][nome][1]
    m = r["teste"][nome]
    p(f"No modelo escolhido, houve {tn} benignos corretamente classificados, {tp} malignos corretamente identificados, {fp} falsos positivos e {fn} falsos negativos. A acurácia foi {m['accuracy']:.2%}, o recall foi {m['recall']:.2%} e o F1 foi {m['f1']:.2%}.")
    p(f"Como referência simples, prever sempre benigno teria acurácia de {r['baseline_accuracy_teste']:.2%} neste teste e recall zero para malignos. A comparação reforça a necessidade de avaliar a classe de interesse, em vez de olhar apenas o total de acertos.")
    p("Os resultados pertencem a uma única divisão de uma base pequena. A diferença entre os modelos não demonstra superioridade em outros hospitais ou populações. Não foram estimados intervalos de confiança nesta versão.")

    pagina()
    titulo("7. Interpretação dos modelos")
    imagem("importancia_arvore.png", largura=13, altura=4.6)
    top = list(r["importancia_top3"])
    p(f"Na árvore, as maiores importâncias foram de {', '.join(top)}. A importância representa a redução de impureza nas divisões do modelo. Ela depende do treino e pode se concentrar em uma variável quando existem outras correlacionadas.")
    imagem("shap_arvore.png", largura=13, altura=4.6)
    p("Foi utilizado TreeExplainer, da biblioteca SHAP, na árvore [3]. O gráfico mostra a média dos valores absolutos de contribuição para a classe maligno nas amostras de validação. Valores maiores indicam maior participação nas previsões; o gráfico agregado não informa a direção de cada efeito. A soma das contribuições com o valor de referência foi conferida contra a probabilidade prevista pela árvore.")
    imagem("coeficientes_logistica.png", largura=13, altura=4.6)
    p("Na regressão logística, os coeficientes foram calculados após a padronização. Sinais positivos favorecem a classe maligno e sinais negativos favorecem benigno, considerando as demais entradas. Correlações entre medidas dificultam atribuir um efeito isolado. Nenhuma dessas interpretações comprova causalidade.")

    pagina()
    titulo("8. Discussão e conclusão")
    p("A solução atendeu à proposta de classificar dados médicos tabulares, comparar dois modelos e avaliar os resultados com conjuntos separados. O pipeline organiza o pré-processamento e evita que os parâmetros de transformação sejam calculados com dados de teste.")
    p(f"A {r['escolhido'].lower()} apresentou o melhor resultado pelo critério de validação adotado. No teste, o resultado mostra potencial para estudos de apoio à análise, mas não permite afirmar que o modelo está pronto para uso clínico.")
    p("A base é histórica, pequena e não representa toda a diversidade de pacientes ou serviços de saúde. O experimento não usa exames de um hospital real, não analisa imagens diretamente e não avalia outras doenças. Também não foi feita validação externa, acompanhamento prospectivo ou calibração das probabilidades.")
    p("Para uma aplicação prática, seria necessário avaliar o desempenho em dados externos representativos, investigar diferenças entre grupos de pacientes e validar o fluxo com profissionais de saúde. O uso de dados reais exigiria proteção de informações pessoais, controle de acesso e acompanhamento dos erros. O sistema poderia sinalizar amostras para revisão, sempre com avaliação e decisão final do médico.")
    titulo("9. Organização e reprodução")
    p("O projeto contém scripts Python, dataset em CSV, resultados, Dockerfile e README com os comandos de execução. O script principal reproduz a análise e salva as métricas e os gráficos. O relatório é gerado a partir dos resultados salvos. Os links do repositório e do vídeo de demonstração estão na capa.")
    titulo("Referências")
    p('[1] Wolberg, W.; Mangasarian, O.; Street, W. Breast Cancer Wisconsin (Diagnostic). UCI Machine Learning Repository, 1995. Licença CC BY 4.0. <link href="https://doi.org/10.24432/C5DW2B" color="#245d80">https://doi.org/10.24432/C5DW2B</link>.', "Pequeno")
    p('[2] Scikit-learn. load_breast_cancer. Documentação da biblioteca. <link href="https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html" color="#245d80">Documentação do carregamento da base</link>.', "Pequeno")
    p('[3] SHAP. TreeExplainer. Documentação da biblioteca. <link href="https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html" color="#245d80">Documentação do TreeExplainer</link>.', "Pequeno")

    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#60747f"))
        canvas.drawString(2.2 * cm, 1.25 * cm, "Tech Challenge - Fase 1 | rm378867")
        canvas.drawRightString(18.8 * cm, 1.25 * cm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(destino), pagesize=(21 * cm, 29.7 * cm),
                            rightMargin=2.2 * cm, leftMargin=2.2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.9 * cm,
                            title="Tech Challenge - Fase 1", author=entrega["nome"])
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("PDF gerado:", destino)
    if not entrega.get("repositorio") or not entrega.get("video"):
        print("Entrega pendente: preencha os links reais em entrega.json e gere o PDF novamente.")


if __name__ == "__main__":
    main()
