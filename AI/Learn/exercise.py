def show_messages(messages):
    for message in messages:
        print (f"{message} is fine")


def send_messages(messages):
    while messages:   
        current_messages = messages.pop(0)
        print (f"{current_messages} trans fine")
        new_list.append(current_messages)
        print (f"now list is {new_list}")

messages = ["1","2","3","4","5"]
new_list = []


