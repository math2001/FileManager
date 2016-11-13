text = 'hel\t/hi'

def get_place_to_complete(text):
    for i, char in enumerate(text):
        if char == '\t': 
            return text[:i], text[i+1:]
    return None

def multisplit(string:str, separators:iter, maxsplit:int=-1, deep:bool=True) -> list:
    def remove_deep_lists(list_of_list):
        list_of_elements = []
        for elements in list_of_list:
            for element in elements:
                list_of_elements.append(element)

        return list_of_elements

    pieces = string.split(separators[0], maxsplit=(maxsplit if deep else -1))
    for nb_split, separator in enumerate(separators[1:], 1):
        if nb_split >= maxsplit:
            return pieces
        for i, piece in enumerate(pieces):
            pieces[i] = piece.split(separator, maxsplit=(maxsplit if deep else -1))
        pieces = remove_deep_lists(pieces)
    return pieces


def isdigit(string):
    try: int(string); 
    except ValueError: return False; 
    else: return True

isdigit('-1')