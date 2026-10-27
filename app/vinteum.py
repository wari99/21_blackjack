"""
Blackjack entre dois jogadores (TCP).

Uso:
    python vinteum.py MINHA_PORTA IP_OPONENTE PORTA_OPONENTE BOOL [--debug]

    BOOL = true  persona Dealer: CONECTA no oponente, escolhe a semente e joga primeiro
    BOOL = false persona Jogador: ESCUTA em MINHA_PORTA e espera o Dealer (IP_OPONENTE e PORTA_OPONENTE são ignorados por ele)
"""
import sys
import conexao
from jogo import jogar

def main():
    porta, ip_op, porta_op, inicia = sys.argv[1:5]
    debug = "--debug" in sys.argv
    host = inicia.lower() == "true"

    con = None
    try:
        if host:
            con = conexao.conectar(ip_op, int(porta_op))
        else:
            con = conexao.aguardar(int(porta))
        jogar(con, host, debug)
    except (ConnectionError, OSError) as e:
        print(f"\nConexão perdida: {e}")
    finally:
        if con:
            con.fechar()

if __name__ == "__main__":
    main()