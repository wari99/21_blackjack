"""Toda a parte de rede (TCP). O resto do programa só usa a classe Conexao."""
import socket
import time

TENTATIVAS_CONEXAO = 30  # o Dealer tenta conectar por 60 s (30*2)

class Conexao:
    """
    Troca de mensagens de texto, uma por linha.
    """

    def __init__(self, sock):
        self.sock = sock
        self.arq = sock.makefile("r", encoding="utf-8")

    def enviar(self, texto):
        self.sock.sendall((texto + "\n").encode())

    def receber(self):
        linha = self.arq.readline()
        if not linha:  # conexão fechada pelo outro lado
            raise ConnectionError("O oponente desconectou.")
        return linha.strip()

    def fechar(self):
        self.arq.close()
        self.sock.close()

def conectar(ip, porta):
    """
    Dealer: tenta conectar até o oponente estar no ar.
    """

    print("Procurando o oponente...")

    for _ in range(TENTATIVAS_CONEXAO):
        try:
            sock = socket.create_connection((ip, porta), timeout=3)
            sock.settimeout(None)  # depois de conectado, espera sem limite
            return Conexao(sock)
        except OSError:
            time.sleep(2)

    raise ConnectionError("Não foi possível conectar ao oponente.")


def aguardar(porta):
    """Jogador: escuta e aceita a conexão do Dealer."""

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", porta))
    srv.listen(1)

    print("Aguardando o Dealer...")

    sock, _ = srv.accept()
    srv.close()

    return Conexao(sock)