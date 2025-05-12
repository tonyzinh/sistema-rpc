# Sistema RPC
  Este projeto implementa um sistema Cliente-Servidor para execução remota de operações matemáticas simples via RPC (Remote Procedure Call) usando Named Pipes no Windows.
  
### Arquivos

- **servidor.py**: Executa operações matemáticas solicitadas pelos clientes.
- **cliente.py**: Envia solicitações de operações ao servidor e exibe o resultado.

### Operações Suportadas

- `soma`: Soma de dois números
- `sub`: Subtração de dois números
- `mul`: Multiplicação de dois números
- `div`: Divisão de dois números (com tratamento para divisão por zero)
- `fat`: Fatorial de um número

### Como Funciona

#### Fluxo de Comunicação

1. O **servidor** cria um pipe nomeado (`\\.\pipe\rpc_req_fifo`) e aguarda conexões.
2. O **cliente** conecta-se ao pipe do servidor, cria seu próprio pipe de resposta e envia uma mensagem contendo:
    - Nome do pipe de resposta do cliente
    - Operação desejada
    - Parâmetros da operação
3. O **servidor** lê a requisição, executa a operação e envia o resultado para o pipe de resposta do cliente.
4. O **cliente** lê o resultado do seu pipe de resposta e exibe ao usuário.

### Como Executar

#### Pré-requisitos

- Python 3.x
- Windows
- Instale as dependências:
```
  pip install pywin32
  ```

### Passo a Passo

1. **Inicie o servidor**
```
  python servidor.py
  ```
  O servidor ficará aguardando requisições.

2. **Execute o cliente**
```
  python cliente.py
  ```
  Você pode executar o cliente de duas formas:

  - **Interativo:**  
    O cliente pedirá a operação e os parâmetros.  
    Exemplo de entrada:
    ```
    soma 3 5
    fat 6
    ```

  - **Via linha de comando:**  
    Passe a operação e os parâmetros diretamente:
    ```
    python cliente.py -o soma -p 3,5
    python cliente.py -o fat -p 6
    ```

### Exemplo de Uso
 - **No terminal 1:**  

    ```
    python servidor.py
    ```
 - **No terminal 2:**  

    ```
    python cliente.py
    Digite: soma 10 20
    Resultado: 30
    ```
 - **Ou:**  

    ```
    python cliente.py -o fat -p 5
    Resultado: 120
    ```
