# Compilador Lisp
Este é um compilador de uma versão simplificada de Lisp implementado em Python usando a biblioteca PLY (Python Lex-Yacc).



# 📋 Tokens – Lisp

## 🔤 Funções de String

| Token Lisp     | Token Interno   | Descrição                                   |
|----------------|-----------------|---------------------------------------------|
| `string=`      | `STRING_EQ`     | Comparação de strings                       |
| `string-equal` | `STRING_EQUAL`  | Comparação de strings (case-insensitive)    |

---

## 🧩 Funções Lisp

| Token Lisp | Token Interno | Descrição                   |
|------------|---------------|-----------------------------|
| `list`     | `LIST`        | Cria uma lista              |
| `cons`     | `CONS`        | Constrói um par             |
| `nil`      | `NIL`         | Valor nulo / lista vazia    |
| `car`      | `CAR`         | Primeiro elemento da lista  |
| `cdr`      | `CDR`         | Resto da lista              |
| `defun`    | `DEFUN`       | Define uma função           |
| `cond`     | `COND`        | Condicional múltiplo        |
| `if`       | `IF`          | Condicional simples         |

---

## ➗ Funções Aritméticas

| Token Lisp | Token Interno | Descrição             |
|------------|---------------|-----------------------|
| `floor`    | `FLOOR`       | Arredonda para baixo |
| `mod`      | `MOD`         | Módulo / resto       |
| `expt`     | `EXPT`        | Exponenciação        |

---

## ⚖️ Funções de Comparação

| Token Lisp | Token Interno | Descrição                                   |
|------------|---------------|---------------------------------------------|
| `eq`       | `EQ`          | Igualdade referencial                       |
| `eql`      | `EQL`         | Igualdade estrutural simples                |
| `equal`    | `EQUAL`       | Igualdade estrutural                        |
| `equalp`   | `EQUALP`      | Igualdade estrutural (case-insensitive)     |

---

## 🔀 Funções Lógicas

| Token Lisp | Token Interno | Descrição          |
|------------|---------------|--------------------|
| `and`      | `AND`         | Conjunção lógica   |
| `or`       | `OR`          | Disjunção lógica   |
| `not`      | `NOT`         | Negação lógica     |

---

## 📊 Tipos de Dados

| Token   | Regex                         | Exemplo               | Descrição            |
|---------|-------------------------------|-----------------------|----------------------|
| `NUM`   | `\d+`                         | `42`, `100`           | Números inteiros     |
| `STRING`| `"[^"]*"`                     | `"hello"`, `"world"` | Strings              |
| `ID`    | `[a-zA-Z_][a-zA-Z_0-9-]*`      | `x`, `my-var`, `_test`| Identificadores      |
| `T`     | `t` (case-insensitive)        | `t`, `T`              | Valor verdadeiro     |

---

## 🔧 Operadores

### Aritméticos

| Token    | Símbolo | Descrição       |
|----------|---------|-----------------|
| `PLUS`   | `+`     | Adição          |
| `MINUS`  | `-`     | Subtração       |
| `TIMES`  | `*`     | Multiplicação   |
| `DIVIDE` | `/`     | Divisão         |

---

### Comparação Numérica

| Token     | Símbolo | Descrição          |
|-----------|---------|--------------------|
| `NUM_EQ`  | `=`     | Igualdade numérica |
| `NUM_NEQ` | `/=`    | Diferença numérica |
| `GT`      | `>`     | Maior que          |
| `GTE`     | `>=`    | Maior ou igual     |
| `LT`      | `<`     | Menor que          |
| `LTE`     | `<=`    | Menor ou igual     |

---

## 🧱 Delimitadores

| Token       | Símbolo | Descrição            |
|-------------|---------|----------------------|
| `LPAREN`    | `(`     | Parêntese esquerdo   |
| `RPAREN`    | `)`     | Parêntese direito    |
| `LBRACKET`  | `[`     | Colchete esquerdo    |
| `RBRACKET`  | `]`     | Colchete direito    |
| `LBRACE`    | `{`     | Chave esquerda       |
| `RBRACE`    | `}`     | Chave direita        |

Caracteres inválidos geram mensagem de erro com número da linha

Lexer salta caracteres inválidos e continua análise

# 📋 Parser (Análise Sintática) – Lisp


### Regra Inicial

```bnf
program → sequence
```

Um programa é definido como uma sequência de blocos de código.
Esta é a regra inicial da gramática.

### Sequência e Blocos de Código

```bnf
sequence → sequence block
sequence → block
```
Uma sequência pode conter vários blocos de código consecutivos.
Internamente, essa sequência é representada como uma lista de blocos.


### Bloco de Código

```bnf
block → function
block → expression

```
Um bloco pode ser:

uma definição de função, ou uma expressão avaliada diretamente.

### Definição de Funções
Sintaxe de Função (defun)
```bnf
function → ( DEFUN ID ( param_list ) expression )
```
A definição de função contém:

- ID: nome da função
- param_list: lista de parâmetros formais
- expression: corpo da função


A lista de parâmetros pode ser vazia ou conter múltiplos identificadores.
Ela é armazenada como uma lista de strings.

### Expressões
Expressão Simples
```bnf
expression → term
```
Uma expressão pode ser apenas um termo.

Expressão Composta
```bnf
expression → ( operation )
```
Expressões compostas são escritas entre parênteses e representam operações Lisp.

