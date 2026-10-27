"""
Multicast UDP para os displays.

Mensagem (texto): "PARTIDA|JOGADOR|SEQ|EVENTO|MAO|PAROU"
    PARTIDA : identificador da partida (usamos a semente do baralho)
    JOGADOR : 0 = Dealer, 1 = Jogador
    SEQ     : número de ordem dos eventos desse jogador (ignora duplicadas)
    EVENTO  : INICIO | COMPRAR | PARAR
    MAO     : mão COMPLETA de quem publicou, ex.: "K,3,5"
    PAROU   : 1 se esse jogador já parou, 0 se ainda está jogando
"""
import socket
import struct
import time

GRUPO = "224.1.1.1"
PORTA = 5007
TTL = 2

def codificar(partida, jogador, seq, evento, mao, parou):
    return f"{partida}|{jogador}|{seq}|{evento}|{','.join(mao)}|{int(parou)}"

def decodificar(texto):
    partida, jogador, seq, evento, mao, parou = texto.split("|")
    return {
        "partida": partida,
        "jogador": int(jogador),
        "seq": int(seq),
        "evento": evento,
        "mao": mao.split(",") if mao else [],
        "parou": parou == "1",
    }

class Publicador:
    """Usado pelo jogador. Se o multicast falhar, o jogo continua normalmente."""

    def __init__(self, partida, jogador):
        self.partida = partida
        self.jogador = jogador
        self.seq = 0
        self.ultima = None  #última mensagem enviada (para reenviar no final)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                  socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

    def _enviar(self, msg):
        try:
            self.sock.sendto(msg, (GRUPO, PORTA))
        except OSError:
            pass

    def publicar(self, evento, mao, parou):
        self.seq += 1
        self.ultima = codificar(self.partida, self.jogador, self.seq,
                                evento, mao, parou).encode()
        for _ in range(2):  #envia 2x: o display ignora a repetida
            self._enviar(self.ultima)

    def repetir(self, vezes=3, intervalo=0.5):
        """Reenvia o último estado (mesmo seq). Se o display já o recebeu, ele
        ignora; se o pacote tinha se perdido, o display se atualiza."""
        if not self.ultima:
            return
        for _ in range(vezes):
            time.sleep(intervalo)
            self._enviar(self.ultima)


def escutar():
    """Usado pelo display: entra no grupo e devolve o socket."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # vários displays
    sock.bind(("", PORTA))

    mreq = struct.pack("=4sl", socket.inet_aton(GRUPO), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1) 

    return sock