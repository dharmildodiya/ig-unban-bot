import random

class ProxyManager:
    def __init__(self, file="proxies.txt"):
        try:
            with open(file, "r") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        except:
            self.proxies = []

    def get_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)
