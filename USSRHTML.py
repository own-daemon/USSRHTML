'''
USSRHTML - это компилятор для языка гипертекстовой разметки (ЯГТР), написанный на python.

Компилятор принимает код на языке ЯГТР и выдает файл с кодом на HTML.

ЯГТР - это фантазия на тему того, что было бы, если бы интернет придумали в СССР. 
Особенность данного языка - все вводимые команды должны быть доступны на стандартной ЙЦУКЕН клавиатуре, 
т.е. для ввода команд не нужно переключаться на английскую раскладку. Кроме того, вместо двойных тегов 
типа <body>...</body> используются команды вида \тело(...), что упрощает набор текста.
'''
# импортируем sys для возможности получения файла с исходным текстом в качестве аргумента
import sys
import datetime

#==============================================================================
def parser(inpStr, log=False):
    """
    Функция разбиения строки на токены
    
    Функция принимает на вход строку, возвращает список токенов, полученных
    из этой строки. Границами токенов могут служить: \, (, ), %, команды,
    символл конца строки и др.
    """
    i = 0
    inpStr += ' '   # Добавим в конец строки для удобства
    tokenList = []  # Список токенов
    s = ''          # Накапливает текущие символы в токен
    while i < len(inpStr)-1:
        if inpStr[i] == '\\':        
#           Если после \ идет \, (, ), %, то добавляем сам символ      
            if inpStr[i+1] in r'\())%':
                s += inpStr[i+1]
                i += 2  # И начинаем новую итерацию
                continue
                
            else:
#               Если перед \ что-то было, добавляем в список токенов 
                if s != '':
                    tokenList.append(s)
                    s = inpStr[i]
                else:
                    s += inpStr[i]
        
#       Если текущий символ (, то        
        elif inpStr[i] == '(':
#           Если в s уже что-то накоплено
            if s != '':
                tokenList.append(s) # Считаем это новым токеном
                s = ''              # и обнуляем s
            tokenList.append(inpStr[i]) # ( добавляем в любом случае
                
        elif inpStr[i] == ')':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
            
        elif inpStr[i] == '%':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
         
#       Если текущий символ конец строки, то добавляем его отдельным токеном
#       Нужно, чтобы правильно работать с комментариями
        elif inpStr[i] == '\n':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
            
        elif (inpStr[i] == ':') and (inpStr[i+1] == ':'):
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i:i+2])
            i += 1
            
        else:
            s += inpStr[i]
            
        i += 1
    
    # Если необходимо, запишем список токенов в файл    
    if log == True:
        f = open('tokenList.txt', 'w') # открываем для записи (writing)
        f.write(str(tokenList)) # записываем текст в файл
        f.close() # закрываем файл
        
    return tokenList
#==============================================================================

#==============================================================================
def attributesParser(inpAtrStr):
    """
    Функция-заглушка. Принимает строку со списком атрибутов,
    возвращает список токенов-атрибутов.    
    """
    atrList = []
    
    atrList.append(inpAtrStr)
    
    return atrList
#==============================================================================

#==============================================================================
def attributesCompiler(atrList):
    """
    Функция-заглушка. Принимает список атрибутов на ЯГТР,
    возвращает строку атрибутов на HTML.    
    """
    
    outAtrStr = ' ' + ''.join(atrList)
    
    return outAtrStr
#==============================================================================

#==============================================================================    
def compiler(STATE, token, statement, outpStr, atrStr):
    """
    Функция получения HTML кода из потока токенов

    Входные параметры: 
        STATE - текущее состояние, 
        token - текущий токен, 
        statement - стек состояний, 
        outpStr - текущее значение выходной строки
        atrStr - текущее значение строки атрибутов
    
    Выходные параметры:
        STATE - новое состояние, 
        outpStr - новое значение выходной строки
        atrStr - новое значение строки атрибутов 
    """
    

 
###############################################################################
    """ Отдельно проверим состояние Комментария - если текущее состояние COMMENT,
    то при любом токене выходная строка не изменится.
    Однако, если текущий токен равен переносу строки '\n', то,
    если стек состояний не пуст, то восстанавливаем последнее состояние,
    иначе - текущим состоянием станет '<html>' """ 

    if STATE == 'COMMENT':
        if token == '\n':
            if len(statement) != 0:
                STATE = statement.pop()
            else:
                STATE = '<html>'
                
        return STATE, outpStr, atrStr

###############################################################################      
    elif STATE == 'ATTRIBUTES':
        """ В этом состоянии идет проверка атрибутов тегов.
        Вход в состояние с помощью токена '::',
        Выход из состояния - с помощью повторного токена '::'.""" 
        if token == '::':
            STATE = statement.pop()
            atrList = attributesParser(atrStr)
            atrStr = attributesCompiler(atrList)
            outpStr += atrStr
            atrStr = ''
        
        else:
            atrStr += token
        return STATE, outpStr, atrStr
            
###############################################################################
    if token == '%':
        """ Считаем комментарием все токены от '%' до конца строки"""
        statement.append(STATE)
        STATE = 'COMMENT'

############################################################################### 
    elif token == '::':
        """ Если текущее состояние неполный тег (напр. '<body'), 
        переходим в состояние ATTRIBUTES, чтобы добавить атрибуты тега.
        В противном случае - просто добавляем токен в выходную строку."""
        
        if STATE in NOT_FULL_TAGS:
            statement.append(STATE)
            STATE = 'ATTRIBUTES'
            atrStr = ''
        else:
            outpStr += token
            
###############################################################################
    elif token == '(':
        """ Если текущее состояние неполный тег (напр. '<body'),
        то дописываем закрывающуюся угловую скобку"""
        if STATE in NOT_FULL_TAGS:
            STATE += '>'
            outpStr += '>'
        return STATE, outpStr, atrStr
        
###############################################################################    
    elif token == ')':
        """ Если текущее состояние '<body>' - дописываем конец файла и 
        закрываем его."""
        if STATE == '<body>':
            outpStr += '</body>\n</html>'
            STATE = 'END'
   
        else:
            if STATE in FULL_TAGS:
                """ Если текущее состояние полный тег (напр. <p>), 
                то закрываем его парным тегом (напр. </p>)"""
                outpStr += FULL_TAGS[STATE]
                STATE = statement.pop()
            
            elif STATE in SINGLE_TAGS:
                """ Если тег одиночный (напр. <br>)"""
                pass
            
            else:
                STATE = 'ERROR'
                print('Отсутствует завершающий тег.')
                
        return STATE, outpStr, atrStr  
        
###############################################################################    
    elif token == '\\голова':
        if STATE == '<html>':
            statement.append(STATE)
            STATE = '<head>'
            outpStr += STATE+'\n'
        else:
            STATE = 'ERROR'
        
    elif token == '\\тело':
        statement.append(STATE)
        STATE = '<body'
        outpStr += STATE
            
    elif token == '\\пар':
        statement.append(STATE)
        STATE = '<p'
        outpStr += STATE
            
    elif token == '\\ж':
        statement.append(STATE)
        STATE = '<b'
        outpStr += STATE
        
    elif token == '\\к':
        statement.append(STATE)
        STATE = '<i'
        outpStr += STATE
        
    elif token == '\\пдч':
        statement.append(STATE)
        STATE = '<u'
        outpStr += STATE
        
    elif token == '\\зч':
        statement.append(STATE)
        STATE = '<s'
        outpStr += STATE
        
    elif token == '\\ссылка':
        statement.append(STATE)
        STATE = '<a'
        outpStr += STATE
        
    elif token == '\\под':
        statement.append(STATE)
        STATE = '<sub'
        outpStr += STATE
        
    elif token == '\\над':
        statement.append(STATE)
        STATE = '<sup'
        outpStr += STATE
            
    else:
        outpStr += token    
        
###############################################################################        
    return STATE, outpStr, atrStr
##==============================================================================

# Начало программы

# Начало компиляции
startTime = datetime.datetime.now()
print(startTime.strftime("%d.%m.%Y %H:%M:%S"), 'Начало компиляции')

# Флаг учпешного завершения процесса
processSucessfull = False

# Проверяем наличие аргумента
if len(sys.argv) > 1:
    # Считываем файл по указанному пути
    try:
        fileName = sys.argv[1]        
        f = open(fileName)
        lines = f.readlines()
        text = ''.join(lines)
        f.close()
    except IOError:
        print('Невозможно открыть файл! Проверьте правильность пути.')
        exit()
        
else:
    print('Ошибка! Путь к файлу не указан!')
    exit()

# Список неполных тегов
NOT_FULL_TAGS = ['<head', '<body', '<p', '<b', '<i', '<u', '<s', '<a', '<sub',
                 '<sup']   
# Словарь парных тегов
FULL_TAGS = {'<html>' : '</html>', 
            '<body>' : '</body>', 
            '<p>' : '</p>',
            '<b>' : '</b>',
            '<i>' : '</i>',
            '<u>' : '</u>',  
            '<s>' : '</s>',
            '<a>' : '</a>',
            '<sub>' : '</sub>',
            '<sup>' : '</sup>'
            }
# Список одиночных тегов            
SINGLE_TAGS = ['<br>', '<hr>']

# Стек состояний
statement = []
STATE = '<html>'

inpStr = text
outpStr = '<html>\n'
tokenList = parser(inpStr, log=True)
atrStr = ''

#print(tokenList)

for token in tokenList:

    STATE, outpStr, atrStr = compiler(STATE, token, statement, outpStr, atrStr)
    if STATE == 'ERROR':
        print('Ошибка! Компиляция завершена аварийно')
        break
    elif STATE == 'END':
        break

if STATE != 'END':
    print('Ошибка! Неожиданный конец файла.')
    exit()

#print(outpStr)

#if processSucessfull == False:
#    print('Ошибка! Неожиданный конец файла.')
    #exit()
    
# Создаем файл с тем же имененем и расширением .html
k = fileName.rfind('.')
if k != -1:
    fout = open(fileName[:k] + '.html', 'w')
else:
    fout = open(fileName + '.html', 'w')
# Записываем в файл 
fout.write(outpStr)
fout.close()

endTime = datetime.datetime.now()
deltaTime = endTime - startTime
print('Процесс успешно завершен через ', deltaTime)


