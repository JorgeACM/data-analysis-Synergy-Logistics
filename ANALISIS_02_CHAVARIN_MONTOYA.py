# %%
# Librerias a importar
import csv
import functools
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import matplotlib.pyplot as plt
# import nympy as np

import seaborn as sns
import matplotlib.pyplot as plt

# %%

# Funcion para graficar los medios de transporte usando pandas
# NOTA: Esta función está comentada en la función main, debe usarse por separado para poder graficar
def plot_transport():
    # Se lee el documento
    df = pd.read_csv('synergy_logistics_database.csv',
                     index_col=0, encoding='utf-8', parse_dates=[5])
    # Copiar el DataFrame
    datos = df.copy()
    datos['year'] = datos['date'].dt.strftime('%Y')
    # Agrupando los datos por año
    datos_year = datos.groupby(['year', 'transport_mode'])

    """
    Primero se grafica los viajes totales de cada medio de transporte por año
    """
    # Contando los viajes de cada medio de transporte por año
    serie = datos_year.count()['total_value']
    # convertir la serie a Data Frame
    dym = serie.to_frame().reset_index()
    # Pivotear la 'tabla'
    dym = dym.pivot('year', 'transport_mode', 'total_value')
    # Graficar
    sns.lineplot(data=dym)

    # %%
    """
    Segundo se grafican las ventas totales de cada medio de transporte por año
    """
    # Sumando las ventas
    ventas = datos_year.sum()
    # Reseteando el index
    ventas = ventas.reset_index()
    # Pivoteando los valores de Index
    dym2 = ventas.pivot('year', 'transport_mode', 'total_value')
    # Graficar
    sns.lineplot(data=dym2)
# %%

"""
Función para la Opción 2
Esta funcion ordena la base de datos de acuerdo al medio de transporte.
Grafica en una gráfica de Pay los medios de transportes utilizados
"""
def opc_2(db):
    # Ordenar los datos de acuerdo al medio de transporte
    #Regresa un arreglo de la forma [[Transporte, ventas, total_value]]
    db_transport = sort_by_keys(db, [7])
    #Ordena los datos de menor a mayor de acuerdo a total_value
    db1 = rutas_transitadas(db_transport, None, 2, False)
    #Agrega una columna de acuerdo al valor porcentual de las ventas de cada ruta 
    # respecto a las ventas totales
    db_plot = valor_rutas(db1, 1)
    # Graficar
    db_plot = plot_directions(db1, "Transport")

    # Obtener el TOP 3 de los medios de transporte
    top_transports = rutas_transitadas(db_transport, 3, 2, True)
    print(top_transports)
    # Obtener el medio de transporte más rezagado
    last_transports = rutas_transitadas(db_transport, 1, 2, False)
    print(last_transports)

"""
Función para obtener el punto 3:
OBtiene los países que generan el 80% de los valores de las exportaciones e importaciones
recibe como parámetros, la base de datos y la dirección a agrupar (Exportaciones o Importaciones)
"""
def opc_3(db, direction):
    # Agrupar los datos de acuerdo a la direccion que puede ser:
    # Exportaciones o Importaciones
    db_direction = sort_by_keys(db, [1])
    # Agrupar ya sea las Exportaciones o Importaciones por país
    db_direction = sort_by_keys(db_direction[direction], [2])
    # Ordenar de mayor a menor la lista de acuerdo al total_value
    db_direction = rutas_transitadas(db_direction, None, 2, True)
    # Obtener una lista con los países que generan el 80% de ingresos junto con el porcentaje de cada uno
    db_direction = valor_rutas(db_direction, .8)
    # Devuelve la lista
    return db_direction

"""
Función para delimitar una lista de acuerdo al porcentaje establecido
Recibo como parámetros, una lista de rutas y el porcentaje donde se desea acortar la lista
"""
def valor_rutas(ruta, per):
    # variable para guardar la suma de todos los total_value
    suma = 0
    # variable para guardar el número de importaciones o exportaciones de cada ruta
    sales = 0
    # Loop para sumar las variables anteriores
    for country in ruta:
        suma += country[2]
        sales += country[1]
    # variable para saber el porcentaje a delimitar
    porcentaje = suma*per
    # Variables para saber la suma de la nueva lista delimitada
    cont = 0
    sum1 = 0
    sales1 = 0
    # Loop donde se delimita la nueva lista
    for country in ruta:
        # sumando los total_value
        sum1 += country[2]
        # contando las ventas
        sales1 += country[1]
        # Se agrega una nueva columna con el porcentaje de cada ruta
        # El 100% es la suma de todos los total_value (la variable suma)
        country.append(country[2]*100/suma)
        # Si sum1 es mayor al porcentaje establecido se termina el loop y se corta la nueva lista
        if sum1 >= porcentaje:
            break
        # contador para saber donde cortar la lista
        cont += 1
    # Saber el porcentaje real
    porc = sum1*100/suma
    # se asigna a una nueva variable la lista cortada
    total_sales = ruta[:cont+1]
    # Si sobraron valores se agrega una nueva fila con el campo "Others"
    if suma-sum1 != 0:
        total_sales.append(['Others', sales - sales1, suma - sum1, 100-porc])
    # Se retorna la nueva lista
    return total_sales

"""
Funcion que compara una columna de dos listas iguales e indica cuál es mayor
"""
def comparacion_rutas(lista1, lista2, col):
    # Sumatoria de la primer lista
    sum1 = 0
    for fila in lista1:
        sum1 += fila[col]
    # Sumatoria de la segunda lista
    sum2 = 0
    for fila in lista2:
        sum2 += fila[col]
    res = sum1 - sum2
    # sum1 es mayor
    if res > 0:
        print('La suma de la primera lista es mayor por: ', res)
        return {'lista_mayor': 1, 'sum1': sum1, 'sum2': sum2, 'res': res}
    # sum2 es mayor
    elif res < 0:
        res *= -1
        print('La suma de la segunda lista es mayor por: ', res)
        return {'lista_mayor': 2, 'sum1': sum1, 'sum2': sum2, 'res': res}
    # ambos son iguales
    elif res == 0:
        print('Las sumatorias de ambas listas son iguales')
        return {'lista_mayor': 0, 'sum1': sum1, 'sum2': sum2, 'res': res}

"""
Función para ver las rutas transitadas, y organizarlas de acuerdo a un valor (sort_by)
y delimitar la lista a un largo qty
"""
def rutas_transitadas(datos, qty, sort_by, sort_reverse):
    # Obtener las llaves de la lista original, es una lista de listas
    keys = datos.keys()
    # Lista donde se almacenarán los datos
    info = []
    # Bucle principal
    for key in keys:
        total = 0
        count = 0
        # Para cada lista dentro de la lista original
        for fila in datos[key]:
            # sumar el total_value
            total = total + fila[9]
            # Agregar una exportaación / importación más
            count += 1
        # Agregarlo a la lista de salida: info
        info.append([key, count, total])
    # Ordena la tabla
    info.sort(key=lambda x: x[sort_by], reverse=sort_reverse)
    # print('{0:^22} - {1:^6} -  {2:^12}'.format('Ruta', 'Envios', 'Valor'))
    # for lista in info[:qty]:
    #     print('{0:<22} - {1:>6} - ${2:>12}'.format(lista[0], lista[1], lista[2]))
    # Si no se establece un limite para la tabla, se devuelve completa
    if qty == None:
        return info
    # En caso contrario se devuelve la lista cortada 
    else:
        return info[:qty]

"""
Función para organizar por valor una lista y convertirla a diccionario
"""
def sort_by_keys(data, cols):
    datos = {}
    # Por cada fila en la lista original:
    for row in data:
        vals = []
        # Indicamos cada una de las columnas que vamos a editar
        for col in cols:
            # if type(row[col]) is int:
            #     row[col] = str(row[col])
            # agregar el valor ubicado en la columna 'col' de la lista original a la nueva lista 'vals'
            vals.append(str(row[col]))
        # Asignar el nombre de la llave para el diccionario, si son varias columnas cada se juntan con un guión
        key = '-'.join(vals)
        # Si la llave no se encuentra aún se agrega la nueva llave
        if key not in datos:
            datos[key] = [row]
        # si ya existe se agrega la lista dentro de esa llave
        else:
            datos[key].append(row)
    # Retorna la nueva lista
    return datos

"""
Función para leer el archivo CSV y eliminar los encabezados
"""
def read_file(name):
    db_arr = []
    # Leer el archivo
    with open(name, 'r') as sldb:
        db = csv.reader(sldb)
        for linea in db:
            # Si el primer dato de la fila es 'direction' quiere decir que es encabezados
            # Se omite
            if(linea[1] == 'direction'):
                continue
                # agregar todos los demás valores
            db_arr.append(linea)
    # Retornar la lista sin encavezados
    return db_arr

"""
Función para convertir en número las columnas que sean necesarias
"""
def convert_to_int(data):
    db = []
    # Recorremos cada dato de cada fila
    for fila in data:
        db_fila = []
        for col in fila:
            # si es digito
            if col.isdigit():
                # Se convierte a entero
                col = int(col)
            db_fila.append(col)
        db.append(db_fila)
    # Devuelve la lista original con los datos necesarios convertidos a enteros
    return db
# 0,            1           2           3       4      5    6               7             8            9
# register_id, direction, origin, destination, year, date, product, transport_mode, company_name, total_value

"""
Funció para graficar a los principales países importadoes y exportadores
"""
def plot_directions(db, direction):
    # lista con los porcentajes de exortaciones/importaciones de cada país
    percent = []
    # lista de países
    countries = []
    per = 0
    # por cada país en la lista original
    for country in db:
        # Se agrega el nombre del país a la lista países
        countries.append(country[0])
        # Se agrega el total de porcentaje de importaciones+exportaciones a la lista porcentajes
        percent.append(country[3])
        # Si el campo del país se llama Others, termianr la iteración
        if country[0] == 'Others':
            continue
        # de lo contrario seguir sumando los porcentajes
        per += country[3]
    # redondear el total del porcentaje a 2 dígitos
    per = str(round(per, 2))
    # Graficar
    plt.pie(x=percent, labels=countries, autopct='%1.2f%%')
    # Titulos de acuerdo a si es Importaciones o Exportaciones
    if direction == 'Imports':
        plt.title('Principales países Importadores')
        plt.show()
        print('Estos países representan el '+per+'% de las importaciones.')
    elif direction == 'Exports':
        plt.title('Principales países Exportadores')
        plt.show()
        print('Estos países representan el '+per+'% de las exportaciones.')
    elif direction == 'Transport':
        plt.title('Medios de transporte utilizados')
        plt.show()

# %%

"""
Funció principal
"""
def main():
    # Leer el archivo y quitar encabezados
    db = read_file('synergy_logistics_database.csv')
    # Convertir las columnas necesarias a número
    db = convert_to_int(db)

    # %%
    # Opción 1) Rutas de importación y exportación
    # Agrupar por ruta (país de origen- pais de destino)
    datos_por_ruta = sort_by_keys(db, [2, 3])
    # Obtener las 10 rutas más demandadas
    ruta1 = rutas_transitadas(datos_por_ruta, 10, 1, True)
    # Obtener las 10 rutas con mayor valor en total_value
    ruta2 = rutas_transitadas(datos_por_ruta, 10, 2, True)
    # Comparar ambas rutas
    comparacion = comparacion_rutas(ruta1, ruta2, 2)
    # Imprimir las 10 rutas más demandadas
    print('Las 10 rutas más demandadas son:')
    for ruta in ruta1:
        print('{:<21} {:^3} {:>13}'.format(ruta[0], ruta[1], ruta[2]))
    print('\n')

    # Imprimir las 10 rutas con mayor valor en total_value
    print('Las 10 rutas con mayor valor monetario son:')
    for ruta in ruta2:
        print('{:<21} {:^3} {:>13}'.format(ruta[0], ruta[1], ruta[2]))
    print('\n')

    """
    Recomendaciones del punto 1
    
    # print('No conviene enfocarse en las rutas más transitadas, pq estas no siempre son las que más valor generan, por ejemplo:')
    # print('La ruta más transitada es Corea del Sur - Vietnam con 497 envíos y un valor de 6,877,007,000')
    # print('Pero la ruta con mayor valor es China - México, con 351 envíos de valor de 12,494,000,000')

    # datos_por_ruta_direccion = sort_by_keys(db, [1,2,3])
    """
    # Obtener el valor de exportaciones e importaciones de China
    datos_pais = sort_by_keys(db, [2, 3])
    tipo = 0
    for ruta in datos_pais:

        if 'China' in ruta:
            for rutita in datos_pais[ruta]:
                tipo += rutita[9]
    print(tipo)

    # Opción 2) Medios de transporte utilizado
    # 3 medios de transporte más importantes de acuerdo al valor de las importaciones y exportaciones
    opc_2(db)
    
    # Opción 3) Valor total de importaciones y exportaciones
    print("Opcion 3")
    db_export = opc_3(db, 'Exports')
    # Grafica de pay de los países que más exportan
    plot_directions(db_export, 'Exports')

    db_import = opc_3(db, 'Imports')
    # Grafica de pay de los países que más importan
    plot_directions(db_import, 'Imports')


if __name__ == '__main__':
    main()