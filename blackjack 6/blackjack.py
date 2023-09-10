import random
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Union

CORAZON = "\u2764\uFE0F"
TREBOL = "\u2663\uFE0F"
DIAMANTE = "\u2666\uFE0F"
ESPADA = "\u2660\uFE0F"
TAPADA = "\u25AE\uFE0F"
FICHAS_INICIALES = 100


@dataclass
class Carta:
    VALORES: ClassVar[list[str]] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    PINTAS: ClassVar[list[str]] = [CORAZON, TREBOL, DIAMANTE, ESPADA]
    pinta: str
    valor: str
    tapada: bool = field(default=False, init=False)

    def calcular_valor(self, as_como_11=True) -> int:
        if self.valor == "A":
            if as_como_11:
                return 11
            else:
                return 1
        elif self.valor in ["J", "Q", "K"]:
            return 10
        else:
            return int(self.valor)

    def __str__(self):
        if self.tapada:
            return f"{TAPADA}"
        else:
            return f"{self.valor}{self.pinta}"


class Mano:

    def __init__(self, cartas: tuple[Carta, Carta]):
        self.cartas: list[Carta] = []
        self.cartas.extend(cartas)

    def es_blackjack(self) -> bool:
        if len(self.cartas) > 2:
            return False
        else:
            return self.cartas[0].valor == "A" and self.cartas[1].valor in ["10", "J", "Q", "K"] \
                    or self.cartas[1].valor == "A" and self.cartas[0].valor in ["10", "J", "Q", "K"]

    def agregar_carta(self, carta: Carta):
        self.cartas.append(carta)

    def calcular_valor(self) -> Union[int, str]:
        for carta in self.cartas:
            if carta.tapada:
                return "--"

        valor = 0

        for carta in self.cartas:
            valor += carta.calcular_valor(valor < 11)

        return valor

    def destapar(self):
        for carta in self.cartas:
            carta.tapada = False

    def limpiar(self):
        self.cartas.clear()

    def __str__(self):
        str_mano = ""
        for carta in self.cartas:
            str_mano += f"{str(carta):^5}"

        return str_mano



class Baraja:

    def __init__(self):
        self.cartas: list[Carta] = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def reiniciar(self):
        self.cartas = [Carta(pinta, valor) for valor in Carta.VALORES for pinta in Carta.PINTAS]

    def revolver(self):
        random.shuffle(self.cartas)

    def repartir_carta(self, tapada=False) -> Optional[Carta]:
        if len(self.cartas) > 0:
            carta = self.cartas.pop()
            carta.tapada = tapada
            return carta
        else:
            return None


@dataclass
class Jugador:
    nombre: str
    fichas: int
    mano: Mano = field(default=None, init=False)

    def inicializar_mano(self, cartas: tuple[Carta, Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)

    def agregar_fichas(self, fichas: int):
        self.fichas += fichas

    def tiene_fichas(self) -> bool:
        return self.fichas > 0

    def puede_apostar(self, cantidad: int):
        return self.fichas >= cantidad


class Casa:

    def __init__(self):
        self.mano: Optional[Mano] = None

    def inicializar_mano(self, cartas: tuple[Carta, Carta]):
        self.mano = Mano(cartas)

    def recibir_carta(self, carta: Carta):
        self.mano.agregar_carta(carta)


class Blackjack:

    def __init__(self):
        self.apuesta_actual: int = 0
        self.jugador: Optional[Jugador] = None
        self.cupier: Casa = Casa()
        self.baraja: Baraja = Baraja()

    def registrar_usuario(self, nombre: str):
        self.jugador = Jugador(nombre, FICHAS_INICIALES)

    def iniciar_juego(self, apuesta: int):
        self.apuesta_actual = apuesta

        self.baraja.reiniciar()
        self.baraja.revolver()

        if self.jugador.mano is not None:
            self.jugador.mano.limpiar()
            self.cupier.mano.limpiar()

        # repartir la mano del jugador
        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta()
        self.jugador.inicializar_mano((carta_1, carta_2))

        # repartir la mano de la casa
        carta_1 = self.baraja.repartir_carta()
        carta_2 = self.baraja.repartir_carta(tapada=True)
        self.cupier.inicializar_mano((carta_1, carta_2))

    def repartir_carta_a_jugador(self):
        self.jugador.recibir_carta(self.baraja.repartir_carta())

    def jugador_perdio(self) -> bool:        
        return self.jugador.mano.calcular_valor() > 21
    

    def destapar_mano_de_la_casa(self):
        self.cupier.mano.destapar()

    def casa_puede_pedir(self) -> bool:
        valor_mano_casa = self.cupier.mano.calcular_valor()
        return valor_mano_casa <= self.jugador.mano.calcular_valor() and valor_mano_casa <= 16

    def repartir_carta_a_la_casa(self):
        self.cupier.recibir_carta(self.baraja.repartir_carta())

    def jugador_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.cupier.mano.calcular_valor()
        return self.jugador.mano.es_blackjack() or valor_mano_jugador > valor_mano_casa or valor_mano_casa > 21 or valor_mano_jugador == 21
    
    def casa_gano(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.cupier.mano.calcular_valor()
        return self.cupier.mano.es_blackjack() or valor_mano_jugador < valor_mano_casa or valor_mano_jugador > 21 or valor_mano_casa == 21

    def hay_empate(self) -> bool:
        valor_mano_jugador = self.jugador.mano.calcular_valor()
        valor_mano_casa = self.cupier.mano.calcular_valor()
        return valor_mano_casa == valor_mano_jugador

def main():
    juego = Blackjack()
    nombre_jugador = input("Ingrese su nombre: ")
    juego.registrar_usuario(nombre_jugador)

    while True:
        apuesta = int(input(f"Apuesta actual: {juego.apuesta_actual}, Fichas disponibles: {juego.jugador.fichas}. Ingrese su apuesta (0 para salir): "))
        
        if apuesta == 0:
            break

        if not juego.jugador.puede_apostar(apuesta):
            print("No tiene suficientes fichas para hacer esa apuesta.")
            continue

        juego.iniciar_juego(apuesta)

        # Verificar si el jugador tiene Blackjack
        if juego.jugador.mano.es_blackjack():
            print("¡Tienes un Blackjack! Ganaste esta ronda.")
            juego.jugador.agregar_fichas(juego.apuesta_actual * 1.5)
            continue  # Salta directamente a la próxima ronda

        while True:
            print(f"\nTu mano: {juego.jugador.mano}, Valor: {juego.jugador.mano.calcular_valor()}")
            print(f"Mano de la casa: {juego.cupier.mano if juego.cupier.mano else '--'}")

            accion = input("¿Qué deseas hacer? (P para pedir, E para esperar): ").upper()

            if accion == 'P':
                juego.repartir_carta_a_jugador()
                if juego.jugador_perdio():
                    print("Te has pasado de 21. Perdiste esta ronda.")
                    break
            elif accion == 'E':
                juego.destapar_mano_de_la_casa()
                while juego.casa_puede_pedir():
                    juego.repartir_carta_a_la_casa()
                print(f"Mano de la casa: {juego.cupier.mano}, Valor: {juego.cupier.mano.calcular_valor()}")
                if juego.jugador_gano():
                    print("¡Ganaste esta ronda!")
                    juego.jugador.agregar_fichas(juego.apuesta_actual)
                elif juego.casa_gano():
                    print("La casa ganó esta ronda.")
                    juego.jugador.agregar_fichas(-juego.apuesta_actual)
                else:
                    print("Es un empate.")
                break
            else:
                print("Opción no válida. Ingresa 'P' o 'E'.")

        if not juego.jugador.tiene_fichas():
            print("Te quedaste sin fichas. Fin del juego.")
            break

if __name__ == "__main__":
    main()