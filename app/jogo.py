"""
Fluxo da partida e mensagens de tela.
"""

import random
from multicast import Publicador
from regras import novo_baralho, pontuar, travada, resultado

def mostrar(nome, mao):
    """
    Exibe o nome do jogador, suas cartas e pontuação total.

    Args:
        nome (str): Nome do jogador.
        mao (list): Lista de cartas que o jogador possui.

    Returns:
        None
    """
    pontuacao = pontuar(mao)

    cartas_formatadas = ", ".join(mao)

    if pontuacao < 0:
        resultado = "ESTOUROU"
    else:
        resultado = pontuacao

    print(f"{nome}: {cartas_formatadas} | TOTAL: {resultado}")

def jogar(conexao, host, debug=False):
    """
    Executa uma partida de Blackjack entre dois jogadores conectados.

    Inicializa a partida, sincroniza o baralho por meio de uma seed compartilhada, 
    distribui duas cartas para cada jogador e controla os turnos de compra e parada até 
    que ambos tenham encerrado suas mãos.

    Args:
        conexao: comunicação entre os jogadores,
        host (bool): Indica se o jogador é o dealer (True) ou o jogador conectado (False).
        debug (bool, optional): Exibe informações sobre as mãos iniciais e as próximas cartas do baralho.
        O padrão é False.

    Returns:
        None

    Raises:
        ValueError: Se a mensagem recebida durante a inicialização não conter semente válida

    Lógica:
        - O Dealer gera a seed e envia ela ao jogador.
        - Os dois jogadores usam mesma semente para gerar baralhos idênticos e manter as ações sincronizadas.
        - Cada jogador pode comprar cartas ou parar sua mão.
        - A partida termina quando os dois jogadores estiverem com as mãos travadas.
        - No fim: exibe as mãos, as pontuações e o resultado da partida.
    """

    minha = 0 if host else 1  # 0 = Dealer 1 = jogador
    outro = 1 - minha

    if host: #handshake: o dealer envia a seed
        seed = random.randint(0, 10**6)
        conexao.enviar(f"INICIO|{seed}")
    else:
        seed = int(conexao.receber().split("|")[1])

    baralho = novo_baralho(seed)
    maos = [[baralho.pop(), baralho.pop()], [baralho.pop(), baralho.pop()]]
    parados = [travada(m) for m in maos]

    #multicast: publica a própria mão inicial nos displays (a seed identifica a partida)
    pub = Publicador(str(seed), minha)
    pub.publicar("INICIO", maos[minha], parados[minha])

    if debug:
        print(f"[DEBUG] Dealer: {maos[0]} | Jogador: {maos[1]}")
        print(f"[DEBUG] Próximas cartas: {baralho[::-1]}")

    print("- - - -  BLACKJACK - - - -\n - - - - - - - - - - - - -")
    print(f"Oponente mostra: {maos[outro][0]} (+ 1 carta oculta)\n")
    if parados[minha]:
        print("Sua mão já está travada.")

    vez = 0 if not parados[0] else 1

    while not all(parados):
        if vez == minha:
            mostrar("* * * * * Você", maos[minha])
            while True:
                r = input("* * * * * Comprar (C) ou parar (P)? ").strip().lower()
                if r in ("c", "p"):
                    break
                print("Opção inválida! Digite 'c' ou 'p'.")
            acao = "COMPRAR" if r == "c" else "PARAR"
        else:
            print("\nAguardando oponente...")
            acao = conexao.receber()

        if acao == "COMPRAR":   #aplica a ação (os dois lados fazem o mesmo e na mesma ordem)
            carta = baralho.pop()
            maos[vez].append(carta)
            parados[vez] = travada(maos[vez])
            if vez == minha:
                print(f"Você recebeu: {carta}")
                if parados[minha]:
                    print("\nSua mão travou.")
            else:
                print(f"Oponente comprou outra carta (tem {len(maos[vez])} em jogo).\n")
        else:
            parados[vez] = True

        if vez != minha and parados[vez]:
            print("Oponente parou.\n")

        if vez == minha:
            conexao.enviar(acao)
            pub.publicar(acao, maos[minha], parados[minha])  #multicast: publica a ação nos displays

        vez = (1 - vez) if not parados[1 - vez] else vez #passa a vez para o outro jogador


    print("\n=== RESULTADO ===")

    mostrar("Você", maos[minha])
    mostrar("Oponente", maos[outro])

    print(resultado(pontuar(maos[minha]), pontuar(maos[outro])))

    pub.repetir() 