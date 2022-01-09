# %%
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


def plot_transport():

    df = pd.read_csv('synergy_logistics_database.csv',
                     index_col=0, encoding='utf-8', parse_dates=[5])
    # No filtro nada
    datos = df.copy()
    # Creo la columna de year_month, que usare como marca
    datos['year'] = datos['date'].dt.strftime('%Y')
    datos_year = datos.groupby(['year', 'transport_mode'])

    # La serie que nos interesa es la de sum para el valor total.
    serie = datos_year.count()['total_value']
    # serrie a df
    dym = serie.to_frame().reset_index()
    # le damos la forma que queremos
    dym = dym.pivot('year', 'transport_mode', 'total_value')
    # Grafico
    sns.lineplot(data=dym)

    # %%
    ventas = datos_year.sum()
    ventas = ventas.reset_index()
    # le damos la forma que queremos
    dym2 = ventas.pivot('year', 'transport_mode', 'total_value')
    # Grafico
    sns.lineplot(data=dym2)
# %%


def opc_2(db):
    db_transport = sort_by_keys(db, [7])
    db1 = rutas_transitadas(db_transport, None, 2, False)
    db_plot = valor_rutas(db1)
    db_plot = plot_directions(db_plot, "Transport")

    top_transports = rutas_transitadas(db_transport, 3, 2, True)
    print(top_transports)
    last_transports = rutas_transitadas(db_transport, 1, 2, False)
    print(last_transports)


def opc_3(db, direction):
    db_direction = sort_by_keys(db, [1])
    db_direction = sort_by_keys(db_direction[direction], [2])
    db_direction = rutas_transitadas(db_direction, None, 2, True)
    db_direction = valor_rutas(db_direction)
    return db_direction


def valor_rutas(ruta):
    suma = 0
    sales = 0
    for country in ruta:
        suma += country[2]
        sales += country[1]
    print('valor total', suma)
    porcentaje = suma*.8
    cont = 0
    sum1 = 0
    sales1 = 0
    for country in ruta:
        sum1 += country[2]
        sales1 += country[1]
        country.append(country[2]*100/suma)
        if sum1 >= porcentaje:
            break
        cont += 1
    porc = sum1*100/suma
    # print(porc)
    total_sales = ruta[:cont+1]
    print('ventas', sum1)
    if suma-sum1 != 0:
        total_sales.append(['Others', sales - sales1, suma - sum1, 100-porc])
    return total_sales


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


def rutas_transitadas(datos, qty, sort_by, sort_reverse):
    keys = datos.keys()
    info = []
    for key in keys:
        total = 0
        count = 0
        for fila in datos[key]:
            total = total + fila[9]
            count += 1
        info.append([key, count, total])
        info.sort(key=lambda x: x[sort_by], reverse=sort_reverse)
    # print('{0:^22} - {1:^6} -  {2:^12}'.format('Ruta', 'Envios', 'Valor'))
    # for lista in info[:qty]:
    #     print('{0:<22} - {1:>6} - ${2:>12}'.format(lista[0], lista[1], lista[2]))
    if qty == None:
        return info[:qty]
    else:
        return info[:qty]


def sort_by_keys(data, cols):
    datos = {}
    for row in data:
        vals = []
        for col in cols:
            # if type(row[col]) is int:
            #     row[col] = str(row[col])
            vals.append(str(row[col]))
        key = '-'.join(vals)
        if key not in datos:
            datos[key] = [row]
        else:
            datos[key].append(row)
    return datos


def read_file(name):
    db_arr = []
    with open(name, 'r') as sldb:
        db = csv.reader(sldb)
        for linea in db:
            if(linea[1] == 'direction'):
                continue
            db_arr.append(linea)
    return db_arr


def convert_to_int(data):
    db = []
    for fila in data:
        db_fila = []
        for col in fila:
            if col.isdigit():
                col = int(col)
            db_fila.append(col)
        db.append(db_fila)
    return db
# 0,            1           2           3       4      5    6               7             8            9
# register_id, direction, origin, destination, year, date, product, transport_mode, company_name, total_value


def plot_directions(db, direction):
    percent = []
    countries = []
    per = 0
    for country in db:
        countries.append(country[0])
        percent.append(country[3])
        if country[0] == 'Others':
            continue
        per += country[3]
    per = str(round(per, 2))
    plt.pie(x=percent, labels=countries, autopct='%1.2f%%')
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


def main():
    db = read_file('synergy_logistics_database.csv')
    db = convert_to_int(db)

    # %%
    # Opción 1) Rutas de importación y exportación
    datos_por_ruta = sort_by_keys(db, [2, 3])
    # print(datos_por_ruta)
    ruta1 = rutas_transitadas(datos_por_ruta, 10, 1, True)
    ruta2 = rutas_transitadas(datos_por_ruta, 10, 2, True)
    comparacion = comparacion_rutas(ruta1, ruta2, 2)
    print('Las 10 rutas más demandadas son:')
    for ruta in ruta1:
        print('{:<21} {:^3} {:>13}'.format(ruta[0], ruta[1], ruta[2]))
    print('\n')
    print('Las 10 rutas con mayor valor monetario son:')
    for ruta in ruta2:
        print('{:<21} {:^3} {:>13}'.format(ruta[0], ruta[1], ruta[2]))
    print('\n')

    # print('No conviene enfocarse en las rutas más transitadas, pq estas no siempre son las que más valor generan, por ejemplo:')
    # print('La ruta más transitada es Corea del Sur - Vietnam con 497 envíos y un valor de 6,877,007,000')
    # print('Pero la ruta con mayor valor es China - México, con 351 envíos de valor de 12,494,000,000')

    # datos_por_ruta_direccion = sort_by_keys(db, [1,2,3])
    datos_pais = sort_by_keys(db, [2, 3])
    tipo = 0
    for ruta in datos_pais:

        if 'China' in ruta:
            for rutita in datos_pais[ruta]:
                tipo += rutita[9]
    print(tipo)

    # Opción 2) Medios de transporte utilizado
    # 3 medios de transporte más importantes de acuerdo al valor de las importaciones y exportaciones
    # plot_transport()
    opc_2(db)

    # db_year = sort_by_keys(db, [4])
    # print(db_year.keys())
    # Opción 3) Valor total de importaciones y exportaciones
    print("Opcion 3")
    db_export = opc_3(db, 'Exports')
    plot_directions(db_export, 'Exports')

    db_import = opc_3(db, 'Imports')
    plot_directions(db_import, 'Imports')


if __name__ == '__main__':
    main()
