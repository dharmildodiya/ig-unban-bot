def log(text):
    with open("logs.txt", "a") as f:
        f.write(text + "\n")
