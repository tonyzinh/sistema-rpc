import math
import signal
import sys
import logging
import atexit
import win32pipe
import win32file
import pywintypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

PIPE_NAME = r'\\.\pipe\rpc_req_fifo'

def soma(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
def div(a, b): return a / b if b != 0 else "Divisão por zero"
def fat(a): return math.factorial(a)

OPERACOES = {
    "soma": soma,
    "sub": sub,
    "mul": mul,
    "div": div,
    "fat": fat,
}

def limpar_recursos():
    try:
        if hasattr(sys, 'pipe_handle'):
            win32pipe.DisconnectNamedPipe(sys.pipe_handle)
            win32file.CloseHandle(sys.pipe_handle)
            logging.info("Pipe do servidor fechado")
    except Exception as e:
        logging.error(f"Erro na limpeza: {e}")

def manipular_sinal(signum, frame):
    logging.info("Encerrando servidor...")
    sys.exit(0)

def inicializar_servidor():
    try:
        sys.pipe_handle = win32pipe.CreateNamedPipe(
            PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            65536, 65536, 0, None)
        
        logging.info(f"Pipe do servidor criado em {PIPE_NAME}")
    except pywintypes.error as e:
        logging.error(f"Erro ao criar pipe: {e}")
        sys.exit(1)

def processar_requisicao(linha):
    try:
        resp_fifo, operacao, parametros = linha.split("|")
        args = list(map(int, parametros.split(",")))
        
        logging.info(f"Requisição: {resp_fifo} | {operacao} | {args}")
        
        if operacao not in OPERACOES:
            resultado = "Operação inválida"
        elif operacao == "fat" and len(args) != 1:
            resultado = "Fatorial requer exatamente 1 parâmetro"
        else:
            resultado = OPERACOES[operacao](*args)
            
        logging.info(f"Resultado: {resultado}")
        
        handle = win32file.CreateFile(
            resp_fifo,
            win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None)
        
        win32file.WriteFile(handle, str(resultado).encode())
        win32file.CloseHandle(handle)
        
    except Exception as e:
        logging.error(f"Erro ao processar requisição: {e}")

def iniciar_loop_servidor():
    logging.info("Servidor RPC ativo. Pressione Ctrl+C para encerrar.")
    
    while True:
        try:
            win32pipe.ConnectNamedPipe(sys.pipe_handle, None)
            result, data = win32file.ReadFile(sys.pipe_handle, 65536)
            linha = data.decode().strip()
            processar_requisicao(linha)
            
            win32pipe.DisconnectNamedPipe(sys.pipe_handle)
            
        except KeyboardInterrupt:
            break
        except pywintypes.error as e:
            if e.winerror == 109:
                logging.warning("Cliente desconectado")
            else:
                logging.error(f"Erro: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    atexit.register(limpar_recursos)
    signal.signal(signal.SIGINT, manipular_sinal)
    inicializar_servidor()
    iniciar_loop_servidor()
