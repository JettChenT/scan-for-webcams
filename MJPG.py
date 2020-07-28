from search import Scanner
check = input("Do you want to check if each footage is completly black/white? This might slow the program down. \n enter yes or no:")
if check == "yes":
    check = True
else:
    check = False
scanner = Scanner()
scanner.MJPG(check)