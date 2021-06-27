from sqlalchemy.orm import Session
from . import models, schemas, tools, options
from datetime import datetime


def buscar_jugador(db: Session, id_jugador):
    """ Función que busca a un jugador por su id """
    # Filtramos la base de datos en busca de una coincidencia
    return db.query(models.Jugador).filter(models.Jugador.id_jugador == id_jugador).first()


def buscar_partida(db: Session, id_partida):
    """ Funcion que busca una partida por su id """
    # Filtramos la base de datos en busca de una coincidencia
    return db.query(models.Partida).filter(models.Partida.id_partida == id_partida).first()


def registrar_jugador(db: Session):
    """ Función que registra a un jugador """
    # Creo el id del jugador
    id_jugador = tools.generar_id(caracteres=14)
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


def registrar_jugador_2(db: Session, datos: schemas.UnirseAPartida):
    """ Función que agrega al jugador 2 a la partida"""
    # Marco el tiempo
    fecha = datetime.now()
    # Actualizo la fecha de ultima partida del jugador y autorizo el paso a actualizar la partida
    if actualizar_jugador(db=db, id_jugador=datos.id_jugador, fecha=fecha):
        # Filtro y modifico
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
                "fecha_ultima_actualizacion": fecha,
            }
        )
        # Guardo los datos
        db.commit()
    return buscar_partida(db=db, id_partida=id_partida)