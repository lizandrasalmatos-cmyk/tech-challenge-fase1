# Passos para concluir a entrega

O código e o relatório estão preparados localmente. A publicação do Git e a gravação do vídeo ainda precisam ser concluídas.

## 1. Criar o repositório

1. Entre na conta `lizandrasalmatos-cmyk` no GitHub.
2. Clique em **+**, depois **New repository**.
3. Nome: `tech-challenge-fase1`.
4. Escolha **Public**, para que o avaliador consiga acessar, e clique em **Create repository**. Se preferir privado, confirme antes como dar acesso ao professor.
5. Clique em **uploading an existing file** ou **Add file > Upload files**.
6. Arraste os arquivos e pastas do projeto. Inclua `src`, `dados`, `resultados`, `output`, README.md, Dockerfile, requirements.txt, entrega.json e os guias. Inclua também `.gitignore` e `.dockerignore`.
7. Não envie `.venv`, `.git`, `tmp` nem o ZIP. O GitHub precisa mostrar os arquivos extraídos, não apenas o ZIP.
8. Clique em **Commit changes**.

Depois de criado, o endereço esperado é `https://github.com/lizandrasalmatos-cmyk/tech-challenge-fase1`. Confira no navegador antes de usá-lo. Esse endereço ainda não é prova de publicação.

## 2. Gravar o vídeo

Use `ROTEIRO_VIDEO.md` como apoio. Grave a tela executando o script e mostrando os resultados. Publique no YouTube como **não listado** ou no Vimeo com acesso permitido ao avaliador. Máximo de 15 minutos. Confira se o link abre para alguém que não está conectado à sua conta.

## 3. Atualizar o relatório

Edite `entrega.json`: mantenha nome e RM e coloque o endereço real do repositório em `repositorio` e o do vídeo em `video`. Preserve as aspas e vírgulas do JSON.

Execute:

```powershell
.venv\Scripts\python.exe src/gerar_relatorio.py
```

O PDF atualizado ficará em `output/pdf/relatorio_tecnico.pdf`. Atualize também `entrega.json` e o PDF no GitHub.

## 4. Conferência final

- Ler o relatório e entender o que foi feito.
- Confirmar nome, RM e links no PDF.
- Abrir o repositório e conferir código, Dockerfile, README, dados e resultados.
- Abrir o vídeo e confirmar duração e permissões.
- Enviar o PDF conforme as instruções do portal da FIAP.

O Dockerfile está incluído, mas a execução com Docker depende de Docker instalado. A validação local do projeto é feita executando os scripts Python.
