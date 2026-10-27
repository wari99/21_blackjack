import random

VALORES = "2 3 4 5 6 7 8 9 10 J Q K A".split()

def novo_baralho(semente):
    baralho = [v for _ in range(4) for v in VALORES]  # 52 cartas, sem Coringas
    random.Random(semente).shuffle(baralho)  # mesma semente = mesma ordem
    return baralho

def pontuar(mao):
    """
    Pontuacao:
    - Á sempre vale 1
    - J, Q e K valem 10
    - -1 = fim de jogo
    """

    pontos = 0
    for carta in mao:
        if carta == "A":
            pontos += 1
        else:
            pontos += 10 if carta in ("J", "Q", "K") else int(carta)
    return pontos if pontos <= 21 else -1

def travada(mao):
    """
    Quando a vez do jogador tem uma parada forçada:
    - 21
    - estouro
    """
    p = pontuar(mao)
    return p >= 21 or p < 0

def resultado(pm, po):
    """
    Recebe as duas pontuções
    Devolve a mensagem final.
    """
    if pm < 0 and po < 0:
        return "Ambos estouraram. Empate."
    if pm < 0:
        return "Você estourou. Oponente venceu."
    if po < 0:
        return "Oponente estourou. Você venceu!"
    if pm > po:
        return "Você venceu!"
    if pm < po:
        return "Oponente venceu!"
    return "Empate!"