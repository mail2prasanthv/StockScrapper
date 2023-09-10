dict = {"z": 1, "b": 2, "c": 3, "d": 4, "e": 5}

sorted_dict = sorted(dict.items(), key=lambda x: x[0])

print(sorted_dict)