import random

class ProxyManager:
    def __init__(self, file="proxies.txt"):
        with open(file, "r") as f:
            self.proxies = [line.strip() for line in f if line.strip()]

    def get_proxy(self):
        return random.choice(self.proxies)
