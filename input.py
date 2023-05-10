def input_choose_piece(position,coord, available_pieces=None ):
    while True:
        
        try:
            if coord.lower() == "x":
                return None
            coordinate = (int(coord) // 10), (int(coord) % 10)
            field = position.get_table()[coordinate[0]][coordinate[1]]
            if available_pieces:
                if coordinate in available_pieces:
                    if position.get_white_to_move() and field.lower() == "b":
                        next_moves = position.find_valid_moves_for_piece(
                            coordinate)
                        if len(next_moves) != 0:
                            return coordinate
                        else:
                            return "Chosen figure has no available moves!"
                    elif not position.get_white_to_move() and field.lower() == "c":
                        return coordinate
                    else:
                        return 'La seleccion de ficha es incorrecta (yes)'
                else:
                    return "Campura forsada"
                        

            else:
                if position.get_white_to_move() and field.lower() == "b":
                    next_moves = position.find_valid_moves_for_piece(
                        coordinate)
                    if len(next_moves) != 0:
                        return coordinate
                    else:
                        return "Chosen figure has no available moves!"
                        
                elif not position.get_white_to_move() and field.lower() == "c":
                    return coordinate
                else:
                    return "La seleccion de ficha es incorrecta."
        except:
            return 'Invalid coordinate! Try again.'
    


def input_choose_field(valid_moves,coord2):
    while True:
        """ coord = input(
            "Enter the field coordinates(row+column without space ex. 70 for down left)<x to exit>:") """
        try:
            if coord2.lower() == "x":
                return None
            coordinate = (int(coord2) // 10), (int(coord2) % 10)
            if coordinate not in valid_moves:
                return "Selection is not valid! Try again."
            else:
                return coordinate
        except:
            return 'Invalid coordinate! Try again.'


def input_forced_moves(forced):
    while True:
        try:
            if forced.lower() == "yes":
                return True
            if forced.lower() == "no":
                return False
            print("Invalid choice! Try again.")

        except:
            print("Invalid input! Try again!")