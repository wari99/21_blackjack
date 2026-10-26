import random
import sys

VALORES = "2 3 4 5 6 7 8 9 10 J Q K A".split()

def novo_baralho():
    baralho = [v + n for n in "♥♣♦♠" for v in VALORES] + ["JOKER", "JOKER"]
    random.shuffle(baralho)
    return baralho

def pontuar(mao):
    """
    Calcula a pontuação de uma mão de cartas.

    Recebe:
        mao: lista de cartas, por exemplo ["K♠", "7♥"] ou ["JOKER", "5♣"].

    Devolve um número inteiro:
        22  Natural 22: exatamente 2 Coringas nas duas primeiras cartas (a mão mais forte do jogo).
        21  21 Rígido (qualquer mão com 1 Coringa) ou 21 normal. -1  -> A mão estourou (passou de 21).
        0 a 20   Soma normal das cartas.

    Observação: 22 e -1 não são pontos reais, são códigos usados
    para o jogo comparar as mãos facilmente.
    """
    
    jokers = mao.count("JOKER")
    if jokers == 2 and len(mao) == 2:
        return 22
    if jokers:
        return 21

    pontos = ases = 0
    for carta in mao:
        v = carta[:-1]
        if v == "A":
            ases += 1
            pontos += 11
        else:
          if v == "J" or v == "Q" or v == "K":
              pontos += 10
          else:
              pontos += int(v)
    while pontos > 21 and ases:
        pontos -= 10
        ases -= 1
    return pontos if pontos <= 21 else -1

def mostrar(nome, mao):
    p = pontuar(mao)
    if p < 0:
        resultado = "ESTOUROU"
    else:
        resultado = p

    cartas = ", ".join(mao)
    print(f"{nome}: {cartas} -> {resultado}")

def mostrar_ordem(baralho):
    """Modo debug: mostra a ordem real de compra (pop tira do fim da lista)."""

    ordem = baralho[::-1]

    print("\n[DEBUG] Ordem de compra:")
    print(f"Jogador (inicial): {ordem[0:2]}")
    print(f"Dealer  (inicial): {ordem[2:4]}")
    print(f"Próximas cartas:   {ordem[4:]}")
    print("-" * 50)

def jogar(debug=False):
    baralho = novo_baralho()
    if debug:
        mostrar_ordem(baralho)
    jogador = [baralho.pop(), baralho.pop()]
    dealer = [baralho.pop(), baralho.pop()]

    print("*** BLACKJACK ***")
    print(f"Dealer mostra: {dealer[0]}")

    while 0 <= pontuar(jogador) < 21:  # 21+ (Rígido/Natural) trava a mão
        mostrar("Você", jogador)
        acao = input("Pedir (P) ou parar (S)? ").strip().lower()
        if acao == "p":
            jogador.append(baralho.pop())
        elif acao == "s":
            break
        else:
            print("Opção inválida! Digite 'p' ou 's'.")

    pj = pontuar(jogador)
    if pj >= 0:
        while 0 <= pontuar(dealer) < 17:
            dealer.append(baralho.pop())
    pd = pontuar(dealer)

    print("\n=== RESULTADO ===")
    mostrar("Você", jogador)
    mostrar("Dealer", dealer)

    if pj < 0:
        print("Você estourou. Dealer venceu.")
    elif pd < 0:
        print("Dealer estourou. Você venceu!")
    elif pj > pd:
        print("Você venceu!" + (" (Natural 22!)" if pj == 22 else ""))
    elif pj < pd:
        print("Dealer venceu!" + (" (Natural 22)" if pd == 22 else ""))
    else:
        print("Empate (push).")


if __name__ == "__main__":
    jogar(debug="--debug" in sys.argv)