import math 

def truncar(numero, casas_decimais):
    fator = 10 ** casas_decimais
    return math.trunc(numero * fator) / fator

def arredondar_para_cima(numero, casas_decimais):
    fator = 10 ** casas_decimais
    return math.ceil(numero * fator) / fator
    
def ganhou(entrada):
    return arredondar_para_cima(1.002991005*entrada, 2)

def perdeu(entrada):
    return arredondar_para_cima(0.98802099*entrada, 2)

def entrada_baseada_na_meta(meta):
    return arredondar_para_cima(meta/1.002991005, 2)

banca_inicial = 150.0
entrada = banca_inicial*2/3
banca_emprestimo = banca_inicial*1/3
comecar = True
entrada_anterior = entrada
emprestimos_banca = []
#32 loss seguidos pra perder
operacoes = ['win', 'loss', 'loss', 'loss', 'loss','loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'loss']
operacoes = operacoes*10
#real = ['win', 'win', 'win', 'loss', 'win', 'win', 'win', 'loss', 'win', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'loss', 'win', 'loss', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'loss', 'loss', 'win', 'win', 'loss']
#real*=3
# operacoes = ['win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win']
real = ['win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'loss', 'win']
real = ['loss', 'loss', 'win', 'win', 'loss', 'loss', 'win', 'loss', 'win']

emprestimos = []
wins = 0
losses = 0


print('--------------------')

for x in real:
    print('entrada:', entrada)
    print('banca de empréstimo: ', banca_emprestimo)
    print('total: ', entrada+banca_emprestimo)
    print('wins: ', wins)
    print('losses: ', losses)
    if x == 'win':
        wins += 1
        if (entrada > (banca_inicial*80/100)) and (banca_emprestimo < (banca_inicial*5/100)):
            banca_inicial = entrada+banca_emprestimo
            banca_emprestimo = banca_inicial*1/3
            entrada = banca_inicial*2/3
            print('banca inicial: ', banca_inicial)
            print('entrada: ', entrada)
        entrada = ganhou(entrada)
        print('meta: ', entrada)
        print('GANHOU!')

    elif x == 'loss':
        losses += 1
        print('PERDEU!')
        sobrou_do_loss = perdeu(entrada)
        quantidade_emprestada = arredondar_para_cima(entrada-sobrou_do_loss, 2)
        print('valor perdido:', quantidade_emprestada)
        print('sobrou da banca: ', sobrou_do_loss)
        emprestimos.append(quantidade_emprestada)
        banca_emprestimo -= quantidade_emprestada
        meta_anterior = ganhou(entrada)
        nova_meta = quantidade_emprestada+meta_anterior
        entrada=entrada_baseada_na_meta(nova_meta)
    
    if banca_emprestimo < 2:
        break
        
    #print(emprestimos)
    print('--------------------')
    print(f'{wins} wins e {losses} losses!')
    print('resultado final: ', entrada+banca_emprestimo)