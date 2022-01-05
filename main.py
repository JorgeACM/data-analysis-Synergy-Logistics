import csv

def rutas_transitadas(datos, qty, sort_by):
    keys = datos.keys()
    info = []
    for key in keys:
        total = 0
        count = 0
        for fila in datos[key]:
            total = total + fila[9]
            count += 1
        info.append([key, count, total])
        info.sort(key=lambda x:x[sort_by], reverse= True)
    return info[:qty]  

def sort_by_keys(data, cols):
    datos = {}
    for row in data:
        vals = []
        for col in cols:
            vals.append(row[col])
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
def main():
    db = read_file('synergy_logistics_database.csv')
    db = convert_to_int(db)
    datos_por_ruta = sort_by_keys(db, [2,3])
    # print(datos_por_ruta)
    rutas = rutas_transitadas(datos_por_ruta, 10, 1)
    print('{0:^22} - {1:^6} -  {2:^12}'.format('Ruta', 'Envios', 'Valor'))
    for lista in rutas:
        print('{0:<22} - {1:>6} - ${2:>12}'.format(lista[0], lista[1], lista[2]))
    rutas = rutas_transitadas(datos_por_ruta, 10, 2)
    print('{0:^22} - {1:^6} -  {2:^12}'.format('Ruta', 'Envios', 'Valor'))
    for lista in rutas:
        print('{0:<22} - {1:>6} - ${2:>12}'.format(lista[0], lista[1], lista[2]))
    print('No conviene enfocarse en las rutas más transitadas, pq estas no siempre son las que más valor generan, por ejemplo:')
    print('La ruta más transitada es Corea del Sur - Vietnam con 497 envíos y un valor de 6,877,007,000')
    print('Pero la ruta con mayor valor es China - México, con 351 envíos de valor de 12,494,000,000')
   # print(rutas)

    datos_por_ruta_direccion = sort_by_keys(db, [1,2,3])
            
            

if __name__ == '__main__':
    main()