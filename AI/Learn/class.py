class Restaurant:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.running = 0
    def desc(self):
        print (f"name is {self.name}")
    def open(self):
        print(f"now is {self.type}")
    def res_running(self):
        print (f"{self.running()}")
    def update_running(self,update):
        if update >= self.running:
            self.running = update
        else:
            print("fail")
    def incremnt_running(self,miles):
        self.running += miles

my_res = Restaurant("DL","Close")
my_res.update_running(23)
my_res.desc()

print(f"the rest opens {my_res.running}")



