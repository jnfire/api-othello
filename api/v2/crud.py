from sqlalchemy.orm import Session
from . import models, schemas, tools, options, game
from datetime import datetime



def buscar_jugador(db: Session, id_jugador):
    """ Función que busca a un jugador por su id """
    # Filtramos la base de datos en busca de una coincidencia
    existe = db.query(models.Jugador).filter(models.Jugador.id_jugador == id_jugador).first()
    # Si existe lo entrego
    if existe:
        return existe
    # Si no existe lo analizo
    else:
        # Si cumple con el numer ode caracteres
        if tools.verificar_id(id_jugador=id_jugador):
            # Guardo los datos del jugador
            db_jugador = models.Jugador(
                id_jugador=id_jugador,
            )
            # Agrego la ficha del jugador a la base de datos
            jugador = tools.guardar_datos(db=db, registro=db_jugador)
            # Devuelvo el id del jugador
            return jugador
        else:
            return False


def buscar_partida(db: Session, id_partida):
    """ Funcion que busca una partida por su id """
    # Filtramos la base de datos en busca de una coincidencia
    return db.query(models.Partida).filter(models.Partida.id_partida == id_partida).first()


def registrar_jugador(db: Session):
    """ Función que registra a un jugador """
    # Creo el id del jugador
    id_jugador = tools.generar_id()
    # Relleno la ficha del jugador
    db_jugador = models.Jugador(
        id_jugador=id_jugador,
    )
    # Agrego la ficha del jugador a la base de datos
    jugador = tools.guardar_datos(db=db, registro=db_jugador)
    # Devuelvo el id del jugador
    return jugador


def registrar_partida(db: Session, datos: schemas.CrearPartida):
    """ Función que registra una partida """
    # Creo el id de la partida
    id = tools.generar_id()
    # Relleno la ficha de la partida
    db_partida = models.Partida(
        id_partida=id,
        id_jugador_1=datos.id_jugador,
        tipo_de_partida=datos.tipo_de_partida,
        tablero=game.tablero_default,
    )
    # Si la partida no es online, cargo el jugador 2 y paso a activa
    if datos.tipo_de_partida == options.Tipo.local or datos.tipo_de_partida == options.Tipo.boot:
        # Agrego que es jugador local
        if datos.tipo_de_partida == options.Tipo.local:
            db_partida.id_jugador_2 = 'local'
        # Agrego que es jugador boot
        elif datos.tipo_de_partida == options.Tipo.boot:
            db_partida.id_jugador_2 = 'boot'
        # Cambio el estado de la partida
        db_partida.estado = options.Estado.activa
    # Guardo los cambios
    partida = tools.guardar_datos(db=db, registro=db_partida)
    # devuelvo el resultado
    return partida


def registrar_partida_revancha(db: Session, datos: schemas.CrearPartida, partida_antigua):
    """ Función que registra una partida """
    # Creo el id de la partida
    id = tools.generar_id()
    # Creo un marcador de fecha
    fecha = datetime.now()
    # Relleno la ficha de la partida
    db_partida = models.Partida(
        id_partida=id,
        tipo_de_partida=options.online,
        estado=options.Estado.espera,
        tablero=game.tablero_default,
    )
    # Compruebo que jugador era en la partida anterior
    if partida_antigua.id_jugador_1 == datos.id_jugador:
        db_partida.id_jugador_2 = datos.id_jugador
    if partida_antigua.id_jugador_2 == datos.id_jugador:
        db_partida.id_jugador_1 = datos.id_jugador
    # Guardo los cambios
    partida = tools.guardar_datos(db=db, registro=db_partida)
    # Actualizo la antigua
    db.query(models.Partida).filter(models.Partida.id_partida == partida_antigua.id_partida).update(
        {
            "nueva_partida": partida.id_partida,
            "fecha_ultima_actualizacion": fecha,
        }
    )
    # Guardo los datos
    db.commit()
    # devuelvo el resultado
    return partida


def registrar_jugador_2(db: Session, datos: schemas.UnirseAPartida):
    """ Función que agrega al jugador 2 a la partida"""
    # Marco el tiempo
    fecha = datetime.now()
    # Actualizo la fecha de ultima partida del jugador y autorizo el paso a actualizar la partida
    if actualizar_jugador(db=db, id_jugador=datos.id_jugador, fecha=fecha):
        # Filtro y modifico
        partida = buscar_partida(db=db, id_partida=datos.id_partida)
        # Compruebo si es una partida de revancha
        if not partida.id_jugador_1:
            db.query(models.Partida).filter(models.Partida.id_partida == datos.id_partida).update(
                {
                    "id_jugador_1": datos.id_jugador,
                    "estado": options.Estado.activa,
                    "fecha_ultima_actualizacion": fecha,
                }
            )
        else:
            db.query(models.Partida).filter(models.Partida.id_partida == datos.id_partida).update(
                {
                    "id_jugador_2": datos.id_jugador,
                    "estado": options.Estado.activa,
                    "fecha_ultima_actualizacion": fecha,
                }
            )
        # Guardo los datos
        db.commit()
    # Entrego los datos de la partida actualizados
    return buscar_partida(db=db, id_partida=datos.id_partida)


def actualizar_jugador(db: Session, id_jugador, fecha):
    """ Función que actualiza los datos del jugador """
    # Filtro y modifico
    db.query(models.Jugador).filter(models.Jugador.id_jugador == id_jugador).update(
        {
            "fecha_ultima_partida": fecha
        }
    )
    # Guardo los datos
    db.commit()
    # Compruebo si se han hecho los cambios
    jugador = buscar_jugador(db, id_jugador=id_jugador)
    # Entrego true si se ha actualizado correctamente
    if jugador.fecha_ultima_partida == str(fecha):
        return True
    # Entrego false si no se ha actualizado correctamente
    else:
        return False


def actualizar_partida(db: Session, id_jugador, id_partida, partida: schemas.EstadoPartida):
    """ Función que actualiza el estado de la partida """
    # Actualizo la fecha y hora de la última partida del jugador
    fecha = datetime.now()
    if actualizar_jugador(db=db, id_jugador=id_jugador, fecha=fecha):
        db.query(models.Partida).filter(models.Partida.id_partida == id_partida).update(
            {
                "estado": partida.estado,
                "turno": tools.nuevo_turno(turno_actual=partida.turno),
                "juega": partida.juega,
                "victoria": partida.victoria,
                "tablero": partida.tablero,
                "contador_jugador_1": partida.contador_jugador_1,
                "contador_jugador_2": partida.contador_jugador_2,
                "fecha_ultima_actualizacion": fecha,
            }
        )
        # Guardo los datos
        db.commit()
    return buscar_partida(db=db, id_partida=id_partida)
