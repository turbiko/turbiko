def isfloat(value):

    # check if value string float
    # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    try:
        float(value)
        return True
    except ValueError:
        return False