import os
import sys
import argparse
import atexit
import logging
import win32file
import win32pipe
import pywintypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SERVER_FIFO = r'\\.\pipe\rpc_req_fifo'
OPERACOES_DISPONIVEIS = ["soma", "sub", "mul", "div", "fat"]

def limpar_recursos():
    pass

def conectar_servidor():
    try:
        return win32file.CreateFile(
            SERVER_FIFO,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None)
    except pywintypes.error as e:
        logging.error(f"Falha ao conectar: {e}")
        sys.exit(1)

def enviar_requisicao(operacao, parametros):
    client_fifo = r'\\.\pipe\rpc_resp_{}'.format(os.getpid())
    resp_pipe = None
    handle = None

    try:
        resp_pipe = win32pipe.CreateNamedPipe(
            client_fifo,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1,
            65536, 65536, 0, None)
        
        logging.debug(f"Pipe de resposta criado em {client_fifo}")

        handle = win32file.CreateFile(
            SERVER_FIFO,
            win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None)
        
        mensagem = f"{client_fifo}|{operacao}|{parametros}".encode()
        win32file.WriteFile(handle, mensagem)

        win32pipe.ConnectNamedPipe(resp_pipe, None)
        
        result, data = win32file.ReadFile(resp_pipe, 4096)
        return data.decode()

    except pywintypes.error as e:
        logging.error(f"Erro de comunicação: {e}")
        return f"Erro: {e}"
    finally:
        if resp_pipe:
            win32file.CloseHandle(resp_pipe)
        if handle:
            win32file.CloseHandle(handle)

def processar_entrada_usuario():
    parser = argparse.ArgumentParser(description='Cliente RPC')
    parser.add_argument('-o', '--operacao', choices=OPERACOES_DISPONIVEIS,
                        help='Operação a ser executada (opcional)')
    parser.add_argument('-p', '--parametros', 
                       help='Parâmetros separados por vírgula (opcional)')
    
    args = parser.parse_args()
    
    if args.operacao and args.parametros:
        return args.operacao, args.parametros
    
    while True:
        try:
            entrada = input("Digite a operação e os parâmetros (ex: soma 3 5): ")
            partes = entrada.split()
            
            if not partes:
                print("Entrada vazia. Tente novamente.")
                continue
            
            operacao = partes[0].lower()
            
            if operacao not in OPERACOES_DISPONIVEIS:
                print(f"Operação inválida. Escolha entre: {', '.join(OPERACOES_DISPONIVEIS)}")
                continue
                
            parametros = ",".join(partes[1:])
            
            if operacao == "fat" and len(partes) != 2:
                print("Fatorial requer exatamente 1 parâmetro")
                continue
            elif operacao != "fat" and len(partes) != 3:
                print("Operações aritméticas requerem exatamente 2 parâmetros")
                continue
                
            return operacao, parametros
            
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

def main():
    atexit.register(limpar_recursos)
    operacao, parametros = processar_entrada_usuario()
    resultado = enviar_requisicao(operacao, parametros)
    print(f"\nResultado: {resultado}")

if __name__ == "__main__":
    main()
