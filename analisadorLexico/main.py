class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

    def __str__(self):
        return f"Token(tipo={self.tipo}, valor='{self.valor}', linha={self.linha})"


class LexicalAnalyzer:
    def __init__(self, arquivo_entrada):
        self.arquivo_entrada = arquivo_entrada
        self.tokens = []
        self.erros = []

        # Definir palavras-chave, operadores e delimitadores
        self.keywords = {'int', 'float', 'boolean', 'if', 'else', 'return', 'while', 'for'}
        self.operators = {'+', '-', '*', '/', '==', '!=', '>', '>=', '<', '<=', '&&', '||', '=', '++', '--', '.'}
        self.delimiters = {';', ',', '(', ')', '{', '}', '[', ']'}

        # Grafo de transições de estado (DFA)
        self.states = {
            'start': {'letter': 'identifier', 'digit': 'number', 'symbol': 'error', 'operator': 'operator', 'delimiter': 'delimiter'},
            'identifier': {'letter': 'identifier', 'digit': 'identifier', '_': 'identifier', 'symbol': 'error', 'operator': 'error', 'delimiter': 'error'},
            'number': {'digit': 'number', '.': 'float_number', 'symbol': 'error', 'operator': 'error', 'delimiter': 'error'},
            'float_number': {'digit': 'float_number', 'symbol': 'error', 'operator': 'error', 'delimiter': 'error'},
            'operator': {'symbol': 'error', 'letter': 'error', 'digit': 'error', '_': 'error', 'operator': 'error', 'delimiter': 'error'},
            'delimiter': {'letter': 'error', 'digit': 'error', '_': 'error', 'symbol': 'error', 'operator': 'error', 'delimiter': 'error'},
            'error': {'letter': 'error', 'digit': 'error', '_': 'error', 'symbol': 'error', 'operator': 'error', 'delimiter': 'error'}
        }

    def ler_arquivo(self):
        try:
            with open(self.arquivo_entrada, 'r') as arquivo:
                return arquivo.readlines()
        except FileNotFoundError:
            self.erros.append("Arquivo não encontrado!")
            return []

    def analisar(self):
        linhas = self.ler_arquivo()
        if not linhas:
            return

        for num_linha, linha in enumerate(linhas, start=1):
            linha = linha.strip()
            if linha.startswith('//') or '/*' in linha:
                continue  # Ignorar comentários

            i = 0
            while i < len(linha):
                char = linha[i]

                if char.isalpha() or char == '_':
                    tipo = 'letter'
                elif char.isdigit():
                    tipo = 'digit'
                elif char in self.operators:
                    tipo = 'operator'
                elif char in self.delimiters:
                    tipo = 'delimiter'
                else:
                    tipo = 'symbol'

                estado_atual = 'start'
                while estado_atual in self.states and tipo in self.states[estado_atual]:
                    proximo_estado = self.states[estado_atual][tipo]
                    if proximo_estado == 'identifier':
                        start = i
                        while i < len(linha) and (linha[i].isalnum() or linha[i] == '_'):
                            i += 1
                        valor = linha[start:i]
                        if valor in self.keywords:
                            self.tokens.append(Token('Keyword', valor, num_linha))
                        else:
                            self.tokens.append(Token('Identifier', valor, num_linha))
                        break
                    elif proximo_estado == 'number':
                        start = i
                        while i < len(linha) and linha[i].isdigit():
                            i += 1
                        if i < len(linha) and linha[i] == '.':
                            i += 1
                            while i < len(linha) and linha[i].isdigit():
                                i += 1
                        valor = linha[start:i]
                        self.tokens.append(Token('Number', valor, num_linha))
                        break
                    elif proximo_estado == 'float_number':
                        start = i
                        while i < len(linha) and linha[i].isdigit():
                            i += 1
                        valor = linha[start:i]
                        self.tokens.append(Token('Number', valor, num_linha))
                        break
                    elif proximo_estado == 'operator':
                        start = i
                        while i < len(linha) and linha[i] in self.operators:
                            i += 1
                        valor = linha[start:i]
                        if valor in self.operators:
                            self.tokens.append(Token('Operator', valor, num_linha))
                        else:
                            self.erros.append(f"Erro léxico na linha {num_linha}: {valor}")
                        break
                    elif proximo_estado == 'delimiter':
                        self.tokens.append(Token('Delimiter', char, num_linha))
                        i += 1
                        break
                    elif proximo_estado == 'error':
                        self.erros.append(f"Erro léxico na linha {num_linha}: {char}")
                        i += 1
                        break
                    else:
                        i += 1

    def salvar_tokens(self, arquivo_saida):
        with open(arquivo_saida, 'w') as arquivo:
            for token in self.tokens:
                arquivo.write(str(token) + '\n')

    def salvar_erros(self, arquivo_erros):
        with open(arquivo_erros, 'w') as arquivo:
            for erro in self.erros:
                arquivo.write(erro + '\n')


# Solicitar ao usuário o nome do arquivo
nome_arquivo = input("Diga o nome do arquivo que contém o código fonte: ")

# Inicializa o analisador léxico com o nome do arquivo fornecido pelo usuário
analisador = LexicalAnalyzer(nome_arquivo)

# Realiza a análise léxica
analisador.analisar()

# Salva os tokens e erros em arquivos separados
analisador.salvar_tokens('tokens.txt')
analisador.salvar_erros('erros.txt')

print("Análise léxica concluída. Tokens e erros foram salvos em 'tokens.txt' e 'erros.txt', respectivamente.")
