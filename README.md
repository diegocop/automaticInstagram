# Automatizador Instagram

Programa que segue perfis no Instagram automaticamente. Ele visita um perfil da sua lista, abre a lista de
**seguidores** desse perfil e clica em **Seguir** nas pessoas que aparecem, com esperas aleatórias entre
cada ação para parecer uso normal. Depois de seguir uma quantidade definida, faz uma pausa e recomeça.

Existe em duas versões, com as mesmas funções:

- **Computador** (Windows ou Linux): abre um navegador Chrome que o programa controla.
- **Android**: usa um navegador dentro do próprio app.

> ⚠️ **Atenção:** o Instagram limita quantas pessoas uma conta pode seguir por hora e por dia. Seguir
> demais pode bloquear temporariamente a ação de seguir ou até a conta. Comece com números baixos
> (por exemplo, 15 a 20 por ciclo e pausa de 60 minutos) e use por sua conta e risco.

---

## Como funciona, passo a passo

1. Você monta uma **lista de perfis alvo**: perfis grandes cujo público tem a ver com o seu.
2. Ao apertar **▶ Iniciar**, o programa entra no Instagram com a sua conta.
3. Ele sorteia um perfil da lista, abre os **seguidores** dele e vai clicando em **Seguir**.
4. Quando chega no número de **Seguir por ciclo**, ele faz a **pausa entre ciclos**.
5. Terminada a pausa, começa outro ciclo com outro perfil sorteado, e assim por diante, até você apertar
   **■ Parar**.

---

## Versão para computador

### Abrir o programa

- **Windows:** abra o `automatizador.exe`.
- **Pelo código (Windows ou Linux):** com o Python 3 instalado, rode uma vez:

  ```bash
  pip install playwright
  playwright install chromium
  ```

  e depois, na pasta do programa:

  ```bash
  python interface.py
  ```

### A tela

**Conta do Instagram**
- **Usuário** e **Senha**: a conta que vai seguir as pessoas.
- **Lembrar senha neste computador**: guarda a senha no arquivo `config.json`. Só marque em um computador
  que é só seu.
- Se deixar usuário e senha **em branco**, o navegador abre na página de login e você entra manualmente.
  Use isso se a conta tiver verificação em duas etapas.
- Depois do primeiro login a sessão fica salva (pasta `userdata`), então normalmente não é preciso entrar
  de novo.

**Perfis alvo**
- Coloque **um perfil por linha**. Vale qualquer formato: `https://www.instagram.com/perfil/`,
  `instagram.com/perfil`, `@perfil` ou só `perfil`. Linhas repetidas são removidas.
- Você pode ter **várias listas** (por exemplo, uma por assunto ou uma por conta). Escolha a lista no
  campo **Lista** e use **Nova**, **Renomear** e **Excluir**. O bot usa a lista que estiver selecionada.

**Configurações**
| Campo | O que faz |
|---|---|
| Seguir por ciclo | Quantos perfis seguir antes de fazer a pausa |
| Pausa entre ciclos | Quantos minutos esperar depois de cada ciclo |
| Espera mínima / máxima | Intervalo de segundos sorteado entre cada ação |
| Navegador invisível | Roda sem mostrar a janela do Chrome. Deixe desmarcado no primeiro uso, para conseguir fazer o login |

**Botões**
- **▶ Iniciar**: salva as configurações e começa.
- **■ Parar**: para o bot. Ele termina a ação atual e fecha o navegador.
- **Salvar configurações**: salva sem iniciar.

**Acompanhando**
- O **status** (à direita dos botões) mostra quantos perfis foram seguidos nesta execução, por exemplo
  `🟢 Rodando · 12 seguidos`. Durante a pausa, mostra até que horas ela vai: `⏸ Pausa até 14:35`.
  Quando a pausa acaba, o computador toca um bipe.
- **Total seguido (todas as execuções)**: soma de tudo que já foi seguido. Fica salvo mesmo fechando o
  programa. O botão **Zerar** recomeça a contagem do zero.
- **Log**: o que o bot está fazendo, com as mensagens **mais recentes em cima**. Também fica salvo no
  arquivo `log.txt`. O botão **Limpar** apaga o log.

Ao fechar a janela com o bot rodando, o programa pergunta se deve parar e sair.

---

## Versão Android

### Instalar

1. Copie o arquivo `app-release.apk` para o celular e abra.
2. Se o Android pedir, permita **instalar apps de fontes desconhecidas**.

### Usar

O app tem duas abas no topo:
- **Configurações**: os mesmos campos da versão de computador (conta, listas de perfis, configurações,
  Iniciar/Parar/Salvar, total seguido e log).
- **Navegador**: mostra o Instagram que o bot está usando. Se deixar usuário e senha em branco, faça o
  login por aqui.

**Trazer as listas do computador:** em **Perfis alvo**, toque em **Importar** e cole o conteúdo do arquivo
`config.json` da versão de computador.

### Rodar com o app minimizado

- Quando o app pedir, permita **Sobrepor a outros apps**. Assim, ao minimizar, o navegador vai para uma
  **janelinha no canto da tela**: arraste para mover e toque para voltar ao app.
- Uma **notificação** fixa mostra o andamento (seguidos nesta execução e o total) e tem o botão **Parar**.
- Durante a pausa entre ciclos a janelinha some. Quando a pausa acaba, chega uma **notificação com som**
  ("Pausa terminada") e a janelinha volta.
- **Tire o app da otimização de bateria** (o app pede isso). Senão o Android pode fechar o bot.
- Com a **tela desligada**, o Android para de desenhar a página e o bot pode falhar até a tela ligar de
  novo. Deixe a tela ligada enquanto ele roda (com o app aberto, a tela não apaga sozinha).

---

## Problemas comuns

| Problema | O que fazer |
|---|---|
| Não consegue entrar na conta | Deixe usuário e senha em branco e faça o login manualmente no navegador |
| "Nenhum botão 'Seguir' nos seguidores" | Normal às vezes: o Instagram esconde a lista. O bot vai para outro perfil sozinho |
| Muitos erros ao clicar / "o clique não teve efeito" | O Instagram provavelmente limitou a conta. Pare o bot por algumas horas e depois diminua o **Seguir por ciclo** ou aumente a **pausa** |
| "A lista está vazia" | A lista selecionada não tem perfis. Escolha outra ou adicione perfis |
| Erro de números nas configurações | Todos os campos precisam ser números inteiros maiores que zero, e a espera mínima não pode ser maior que a máxima |
