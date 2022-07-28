from random import randint


class BoardOutException(Exception):
    pass


class DotTypeError(Exception):
    pass


class OccupiedDotException(Exception):
    pass


class IllegalCharException(Exception):
    pass


class Dot:
    def __init__(self, x: int, y: int):
        self.x = x
        if self.x < 1 or self.x > 6:
            raise DotTypeError("x value is out of bounds")
        self.y = y
        if self.y < 1 or self.y > 6:
            raise DotTypeError("y value is out of bounds")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def get_dot(self):
        return print(f'x: {self.x}; y: {self.y}')


class Ship:
    def __init__(self, length: int, bow: Dot, horizontal: bool):
        # We assume that ships always face the right or bottom side of the board
        self.length = length
        self.bow = bow
        self.horizontal = horizontal
        self.lives = length

    @property
    def dots(self):
        dot_list = []
        for i in range(self.length):
            if self.horizontal:
                dot_list.append(Dot(self.bow.x - i, self.bow.y))
            else:
                dot_list.append(Dot(self.bow.x, self.bow.y - i))
        return dot_list


class Board:
    def __init__(self, hid: bool):
        char_map = [[]]
        _list = ["Z"]
        for i in range(1, 7):
            for j in range(1, 7):
                _list.append("O")
            char_map.append(_list)
            _list = ["Z"]
        self.char_map = char_map
        self.fleet = []
        self.hid = hid
        self.ships_intact = 0

    def add_ship(self, length):
        if length not in [1, 2, 3]:
            raise ValueError("Invalid length")
        # print("Adding a ship of length =", length)
        bow = Dot(randint(1, 6), randint(1, 6))
        # bow.get_dot()
        if 1 > bow.x > 6:
            raise BoardOutException("x is out of bounds")
        elif 1 > bow.y > 6:
            raise BoardOutException("y is out of bounds")
        elif self.char_map[bow.x][bow.y] == "■":
            raise OccupiedDotException("This dot is occupied by another ship")
        elif self.char_map[bow.x][bow.y] == "T":
            raise OccupiedDotException("This dot is too close to another ship")
        elif self.char_map[bow.x][bow.y] != "O":
            raise OccupiedDotException("This dot has an illegal character")
        if length == 1:
            hor = False
            new_ship = Ship(length, bow, hor)
        else:
            hor = bool(randint(0, 1))
            for i in range(1, length):
                if hor:
                    if bow.x - i < 1:
                        raise BoardOutException("Ship goes out of bounds")
                    elif self.char_map[bow.x - i][bow.y] != "O":
                        raise OccupiedDotException("Ship tries to occupy illegal dots")
                else:
                    if bow.y - i < 1:
                        raise BoardOutException("Ship goes out of bounds")
                    elif self.char_map[bow.x][bow.y - i] != "O":
                        raise OccupiedDotException("Ship tries to occupy illegal dots")
            new_ship = Ship(length, bow, hor)
        ship_dots = new_ship.dots
        for i in ship_dots:
            # i.get_dot()
            self.char_map[i.x][i.y] = "■"
        self.fleet.append(new_ship)
        self.ships_intact += 1

    def contour(self, ship: Ship, char="T"):
        ship_dots = ship.dots
        adjacent = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (1, -1), (1, 0), (1, 1)]
        for d in ship_dots:
            for i, j in adjacent:
                if 1 <= d.y + j <= 6:
                    if 1 <= d.x + i <= 6 and self.char_map[d.x + i][d.y + j] not in ["■", "X"]:
                        self.char_map[d.x + i][d.y + j] = char

    def board_print(self):
        print(" |1|2|3|4|5|6|")
        for j in range(1, 7):
            print(j, end="|")
            for i in range(1, 7):
                if self.char_map[i][j] == "■" and self.hid:
                    print("O", end="|")
                else:
                    print(self.char_map[i][j], end="|")
            print("\n", end="")
        print("")

    @staticmethod
    def out(_dot: Dot):
        return not(1 <= _dot.x <= 6 and 1 <= _dot.y <= 6)

    def shot(self, _x, _y):
        _dot = Dot(_x, _y)
        # print(f'Targeting x = {_x}; y = {_y}')
        if self.char_map[_x][_y] == "T":
            raise OccupiedDotException("This dot is confirmed to be empty")
        elif self.char_map[_x][_y] == "X":
            raise OccupiedDotException("You have already shot there")
        elif self.char_map[_x][_y] in ["O", "■"]:
            print(f'({_x}; {_y})', end=": ")
            if self.char_map[_x][_y] == "O":
                self.char_map[_x][_y] = "T"
                print("Miss!")
                self.board_print()
                print("Player change")
                pause = input("Press Enter when ready for the next move\n>")
                return False
            elif self.char_map[_x][_y] == "■":
                self.char_map[_x][_y] = "X"
                ships_checked = 0
                for i in self.fleet:
                    if _dot in i.dots():
                        i.lives -= 1
                        if i.lives:
                            print("Hit!")
                            if ships_checked == self.ships_intact and self.ships_intact:
                                raise ValueError("Could not find a ship with this dot")
                            break
                        else:
                            print("Sunk!")
                            self.ships_intact -= 1
                            self.contour(i)
                            if ships_checked == self.ships_intact + 1 and self.ships_intact:
                                raise ValueError("Could not find a ship with this dot")
                            break
                    else:
                        if i.lives:
                            ships_checked += 1

                if self.ships_intact:
                    self.board_print()
                    print("Shot successful, another move is allowed!")
                    pause = input("Press Enter when ready\n>")
                    return True
                else:
                    print("All ships destroyed!")
                    return False
            else:
                raise IllegalCharException("The dot probably contains an illegal character")


class Player:
    def __init__(self, own_board: Board, opponent_board: Board):
        self.own_board = own_board
        self.opponent_board = opponent_board

    def ask(self):
        pass

    # Two different types of move() are used: for the AI player, it does not print anything when exceptions are handled.
    # For a human player, move() prints prompts when the player enters wrong coordinates.
    def move(self):
        pass


class AI(Player):
    def ask(self):
        while True:
            _x, _y = randint(1, 6), randint(1, 6)
            if Board.out(Dot(_x, _y)):
                raise BoardOutException("Targeting the dot out of bounds")
            else:
                break
        return [_x, _y]

    def move(self):
        while True:
            try:
                _x, _y = self.ask()
                hit = self.opponent_board.shot(_x, _y)
            except BoardOutException:
                pass
            except OccupiedDotException:
                pass
            except IllegalCharException:
                pass
            except ValueError:
                pass
            else:

                if not hit:
                    break


class User(Player):
    def ask(self):
        while True:
            _x, _y = input("Enter target coordinates (x, y)\n>").split()
            _x = int(_x)
            _y = int(_y)
            if Board.out(Dot(_x, _y)):
                raise BoardOutException("Targeting the dot out of bounds")
            else:
                break
        return [_x, _y]

    def move(self):
        while True:
            try:
                _x, _y = self.ask()
                hit = self.opponent_board.shot(_x, _y)
            except BoardOutException:
                print("The dot is out of bounds, trying to shoot again...")
            except OccupiedDotException:
                print("The target dot is already shot")
            except IllegalCharException:
                print("The dot contains an illegal character.")
            except ValueError:
                print("Enter 2 numbers separated by space")
            except DotTypeError:
                print("Coordinates must be from 1 to 6")
            else:

                if not hit:
                    break


class Game:
    def __init__(self):
        self.usr_board = Board(False)
        self.ai_board = Board(True)
        self.usr = User(self.usr_board, self.ai_board)
        self.ai = AI(self.ai_board, self.usr_board)

    @staticmethod
    def random_board(hid: bool):
        if hid:
            brd = Board(True)
        else:
            brd = Board(False)
        exception_limit = 1000
        while True:
            exception_counter = 0
            for i in range(7):
                exception_counter = 0
                while True:
                    if not i:
                        length = 3
                    elif i in [1, 2]:
                        length = 2
                    else:
                        length = 1
                    try:
                        brd.add_ship(length)
                    except BoardOutException:
                        # print("Tried to form ship that goes out of bounds, repeating...")
                        exception_counter += 1
                        if exception_counter >= exception_limit:
                            break
                    except OccupiedDotException:
                        # print("The dot appears to be occupied")
                        exception_counter += 1
                        # print(exception_counter)
                        # brd.board_print()
                        if exception_counter >= exception_limit:
                            brd = Board(hid)
                            break
                    else:
                        brd.contour(brd.fleet[i])
                        break
                if exception_counter >= exception_limit:
                    break
            if exception_counter < exception_limit:
                break
        for j in brd.fleet:
            brd.contour(j, "O")
        return brd

    @staticmethod
    def greet():
        pause = input('''
****************************
 Welcome to 6x6 Battleship!
****************************
This is a game of Battleship
played on 6x6 boards
with fleets of 7 ships,
    one with 3 squares,
    two with 2 squares
    and four of 1 square.
****************************
x coordinate:
    represents columns
        (on the top);
y coordinate:
    represents rows
        (on the left).
Coordinates,
    when entered,
        separated by space.
x goes first,
    followed by y.
****************************
"O": unchecked square;
"T": no ship there,
    appears after
        missed shots
        or elimination
        after sinking;
"X": hit square;
"■": intact ship square:
    they should not appear
    on the AI's board.
****************************
By the way,
    the AI is a bit dumb:
    it just shoots
    all over the place,
    so don't be harsh on it!

"I'll be beta, pwomise!"
        --AI (allegedly)
****************************
Press Enter
    to generate game boards.
****************************
>''')

    def loop(self):
        while True:
            self.usr_board = Game.random_board(False)
            self.ai_board = Game.random_board(True)
            self.usr = User(self.usr_board, self.ai_board)
            self.ai = AI(self.ai_board, self.usr_board)
            print("Your board")
            self.usr_board.board_print()
            print("AI board")
            self.ai_board.board_print()
            pause = input("Enter to start\n>")
            while True:
                print("User move")
                self.ai_board.board_print()
                self.usr.move()
                if not self.ai_board.ships_intact:
                    print("You win!")
                    break
                print("AI move")
                self.ai.move()
                if not self.usr_board.ships_intact:
                    print("AI wins!")
                    break
            stop = input("Enter N to stop, any other character to start a new game.\n>")
            stop = stop.lower()
            if "n" in stop:
                break

    def start(self):
        Game.greet()
        self.loop()


if __name__ == "__main__":
    game = Game()
    game.start()
