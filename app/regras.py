"""Regras do blackjack com Coringas. Sem print, input ou rede."""
import random

VALORES = "2 3 4 5 6 7 8 9 10 J Q K A".split()


def novo_baralho(seed):
    """
    Cria e embaralha um baralho de cartas.

    O baralho contém quatro cópias dos valores definidos em
    VALORES e dois JOKERs

    Args:
        seed (int): Valor usado para reproduzir o embaralhamento das cartas

    Returns:
        list: Lista de cartas embaralhadas.
    """
    baralho = []
    naipe = 0

    while naipe < 4:
        for valor in VALORES:
            baralho.append(valor)
        naipe += 1
    baralho.extend(["JOKER", "JOKER"])

    random.Random(seed).shuffle(baralho)

    return baralho


def pontuar(mao):
    """
    22 = Natural 22,
    21 = 21 ou 21 Rígido (Coringa), 
    -1 = estourou.
    """

    jokers = mao.count("JOKER")

    if jokers == 2 and len(mao) == 2: 
        return 22
    if jokers: 
        return 21
    
    pontos = ases = 0

    for carta in mao:
        if carta == "A":
            ases += 1
            pontos += 11
        else:
            pontos += 10 if carta in ("J", "Q", "K") else int(carta)

    while pontos > 21 and ases:
        pontos -= 10
        ases -= 1

    return pontos if pontos <= 21 else -1


def travada(mao):
    """
    Forçar o travamento da mão do jogador: 
    - 21, 
    - Natural 22 
    - Estouro da pontuação
    """
    p = pontuar(mao)
    return p >= 21 or p < 0


def resultado(pm, po):
    """
    Recebimento da pontuação do jogador e oponente 
    Retorna a mensagem final
    """
    if pm < 0 and po < 0:
        return "Ambos estouraram. Empate."
    if pm < 0:
        return "Você estourou. Oponente venceu."
    if po < 0:
        return "Oponente estourou. Você venceu!"
    if pm > po:
        return "Você venceu!" + (" (Natural 22!)" if pm == 22 else "")
    if pm < po:
        return "Oponente venceu!" + (" (Natural 22)" if po == 22 else "")
    return "Empate (push)."