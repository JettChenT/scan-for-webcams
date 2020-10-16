from search import Scanner
check = input("Do you want to check if each footage is completly black/white? This might slow the program down. \n enter yes or no:")
if check == "yes":
    check = True
else:
    check = False

tag = input("Do you want to generate description of the image?\n"
            "enter yes or no:")

if tag == "yes":
    tag = True
else:
    tag = False

scanner = Scanner()
scanner.webcamSeven(check,tag)