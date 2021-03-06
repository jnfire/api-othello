from typing import List, Optional
from pydantic import BaseModel
from . import options


""" Modelos para ver """

class Pong(BaseModel):
    response: str = "pong"

class Jugador(BaseModel):
    """ Dato que recibiremos cuando solicitemos crear un nuevo jugador """
    id_jugador: str


class Partida(BaseModel):
    """ Dato que recibiremos cuando solicitemos crear una partida """
    id_partida: str
    fecha_ultima_actualizacion: Optional[str] = None


class EstadoPartida(BaseModel):
    """ Datos que recibimos cuando pedimos ver una partida o cuando efecutamos un cambio a raiz de un cambio de turno """
    estado: int
    turno: int
    juega: int
    victoria: Optional[int] = None
    tablero: Optional[str] = None
    contador_jugador_1: int = 2
    contador_jugador_2: int = 2
    nueva_partida: str = None
    fecha_ultima_actualizacion: Optional[str] = None


class EstadoPartidaRevancha(BaseModel):
    """ Datos que recibimos cuando pedimos ver una partida o cuando efecutamos un cambio a raiz de un cambio de turno """
    id_partida: str
    estado: int
    turno: int
    juega: int
    victoria: Optional[int] = None
    tablero: Optional[str] = None
    id_jugador_1: str = None
    id_jugador_2: str = None
    contador_jugador_1: int = 2
    contador_jugador_2: int = 2
    fecha_ultima_actualizacion: Optional[str] = None


""" Modelos para modificar """

class CrearPartida(BaseModel):
    """ Datos necesarios para crear una nueva partida """
    tipo_de_partida: int
    id_jugador: str


class UnirseAPartida(BaseModel):
    """ Datos necesarios para unirse a una partida existente """
    id_partida: str
    id_jugador: str


class ColocarFicha(BaseModel):
    """ Datos necesarios para que el servidor calcule la jugada """
    turno: int
    pos_x: int
    pos_y: int
    ficha: int
    juega: options.Juega
    tablero: str
    fecha_ultima_actualizacion: str
