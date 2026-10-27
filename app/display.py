"""
Display: escuta o grupo multicast e mostra a partida, incluindo as cartas
que cada jogador mantém ocultas do oponente.

Uso:
    python3 display.py
(pode abrir quantos displays quiser; ESC ou X encerram)
"""
import os
import socket
import sys

import multicast
from regras import pontuar

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty
    import select

NOMES = {0: "Dealer ", 1: "Jogador"}
TECLAS_SAIR = ("\x1b", "x", "X")  # ESC, x, X


class Teclado:
    """Lê teclas sem bloquear (funciona no Windows e no Linux)."""

    def __enter__(self):
        self.ativo = sys.stdin.isatty()
        if self.ativo and os.name != "nt":
            self.antigo = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())  # lê tecla sem esperar Enter
        return self

    def __exit__(self, *args):
        if self.ativo and os.name != "nt":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.antigo)

    def ler(self):
        """Devolve a tecla pressionada ou None se não houver nenhuma."""
        if not self.ativo:
            return None
        if os.name == "nt":
            if not msvcrt.kbhit():
                return None
            tecla = msvcrt.getwch()
            if tecla in ("\x00", "\xe0"):  # setas/F1..F12 mandam 2 caracteres
                msvcrt.getwch()
                return None
            return tecla
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None
        dados = os.read(sys.stdin.fileno(), 32).decode(errors="ignore")
        if dados.startswith("\x1b") and len(dados) > 1:
            return None  # seta (ESC + [ + letra), não é o ESC sozinho
        return dados[0] if dados else None


def total(mao):
    p = pontuar(mao)
    return "ESTOUROU" if p < 0 else p


def veredito(p0, p1):
    if p0 < 0 and p1 < 0:
        return "Ambos estouraram. Empate."
    if p0 < 0:
        return "Jogador venceu (Dealer estourou)."
    if p1 < 0:
        return "Dealer venceu (Jogador estourou)."
    if p0 > p1:
        return "Dealer venceu!" + (" (Natural 22)" if p0 == 22 else "")
    if p0 < p1:
        return "Jogador venceu!" + (" (Natural 22)" if p1 == 22 else "")
    return "Empate (push)."


def quem_joga(estado, ultima):
    """De quem é a vez, repetindo a regra do jogo. None = ninguém (fim)."""
    parou = [bool(estado.get(j)) and estado[j]["parou"] for j in (0, 1)]
    if all(parou):
        return None
    j = ultima["jogador"]
    if ultima["evento"] == "INICIO":  # cartas distribuídas: o Dealer começa
        return 0 if not parou[0] else 1
    return (1 - j) if not parou[1 - j] else j


def status(e, j, vez):
    if pontuar(e["mao"]) < 0:
        return "ESTOUROU"
    if e["parou"]:
        return "PAROU"
    return "jogando" if vez == j else "aguardando"


def desenhar(estado, turno, vez):
    print("\n" + "=" * 50)
    print("INÍCIO" if turno == 0 else f"TURNO {turno}")
    for j in (0, 1):
        e = estado.get(j)
        if e is None:
            print(f"{NOMES[j]}: (aguardando as cartas...)")
            continue
        print(f"{NOMES[j]}: {', '.join(e['mao'])} | TOTAL: {total(e['mao'])}"
              f" | {status(e, j, vez)} | último: {e['evento']}")
    if all(estado.get(j) and estado[j]["parou"] for j in (0, 1)):
        p0, p1 = (pontuar(estado[j]["mao"]) for j in (0, 1))
        print("--- FIM --- " + veredito(p0, p1))


def main():
    sock = multicast.escutar()
    sock.settimeout(0.2)  # acorda rápido para checar o teclado
    print(f"Display escutando {multicast.GRUPO}:{multicast.PORTA} (ESC ou X para sair)")
    partidas = {}  # partida -> {jogador -> última mensagem}

    try:
        with Teclado() as teclado:
            while True:
                if teclado.ler() in TECLAS_SAIR:
                    break

                try:
                    dados, _ = sock.recvfrom(1024)
                except (socket.timeout, ConnectionResetError):
                    continue
                try:
                    msg = multicast.decodificar(dados.decode())
                except ValueError:
                    continue  # mensagem que não é do nosso jogo

                if msg["partida"] not in partidas:  # primeira vez que vemos essa partida
                    print(f"\n***** PARTIDA {msg['partida']} *****")
                estado = partidas.setdefault(msg["partida"], {})

                atual = estado.get(msg["jogador"])
                if atual and msg["seq"] <= atual["seq"]:
                    continue  # duplicada ou antiga
                estado[msg["jogador"]] = msg

                # Abertura: espera o INICIO do outro lado, para a 1ª tela já
                # mostrar as duas mãos (um deles sempre chega alguns ms antes)
                if msg["evento"] == "INICIO" and len(estado) < 2:
                    continue

                # Turno = eventos até agora (o seq de cada jogador já conta o
                # INICIO como 1). O primeiro evento é o "INÍCIO" (turno 0).
                turno = max(0, sum(e["seq"] for e in estado.values()) - 1)
                desenhar(estado, turno, quem_joga(estado, msg))
    except KeyboardInterrupt:
        pass
    print("\nDisplay encerrado.")


if __name__ == "__main__":
    main()