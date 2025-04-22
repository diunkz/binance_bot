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


#32 loss seguidos pra perder
operacoes = ['win', 'loss', 'loss', 'loss', 'loss','loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'loss']
# operacoes = operacoes*10
# real = ['win', 'win', 'win', 'loss', 'win', 'win', 'win', 'loss', 'win', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'loss', 'win', 'loss', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'win', 'win', 'win', 'loss', 'loss', 'win', 'win', 'loss']
#real*=3
# operacoes = ['win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win', 'win', 'loss', 'loss', 'loss', 'loss', 'loss', 'win']
# real = ['win', 'win', 'win', 'win', 'win', 'loss', 'win', 'win', 'loss', 'win']
# real = ['loss', 'loss', 'win', 'win', 'loss', 'loss', 'win', 'loss', 'win']

teste = ['win', 'win']
loss = ['loss'] * 18
teste = loss + ['win']

emprestimos = []
wins = 0
losses = 0

banca_total = 150

print('--------------------')

banca_para_entradas = banca_total*2/3
banca_para_emprestimo = banca_total*1/3

banca_total = 1000
banca_para_entradas = 100
banca_total = banca_total-banca_para_entradas

print('BTotal', banca_total)
print('BEntrada:', banca_para_entradas)
print('Os dois', banca_total+banca_para_entradas)
qtdloss = 0
for x in teste:
    if x == 'win':
        banca_para_entradas = ganhou(banca_para_entradas)
        print('ganhou')
        qtdloss = 0
    elif x == 'loss':
        qtdloss += 1
        print('perdeu')
        banca_para_entradas = perdeu(banca_para_entradas)
        print('perdeu banca entrada', banca_para_entradas)
        valor_para_pegar_da_banca_total = (banca_para_entradas*(qtdloss*2.5/100))
        print('valor pegar da banca', valor_para_pegar_da_banca_total)
        banca_total -= valor_para_pegar_da_banca_total
        banca_para_entradas += valor_para_pegar_da_banca_total
    print('BTotal', banca_total)
    print('BEntrada:', banca_para_entradas)
    print('Os dois', banca_total+banca_para_entradas)