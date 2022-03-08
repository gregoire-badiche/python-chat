from pynput.keyboard import Listener, Key

class __Choice():

    def __call__(self, question:str, choices:list[str]) -> tuple[int, str]:

        self.selected_value = 0
        self.question = question
        self.choices = choices

        print(question, end=' : ')
        for i in choices:
            print(i, end=' ')
        print('')

        

        self.update()

        with Listener(on_press=self.onkeypress) as self.listener:
            self.listener.join()
        
        return (self.selected_value, self.choices[self.selected_value])

    def update(self):
        print(' ' * (len(self.question) + 3), end='')
        for i in range(self.selected_value):
            print(' ' * len(self.choices[i]), end='')
            print(' ', end='')
        print(' ' * (len(self.choices[self.selected_value]) // 2), end='')
        print('^', end='')
        print(' ' * (len(self.choices[self.selected_value]) - (len(self.choices[self.selected_value]) // 2)), end='')
        for i in range(self.selected_value + 1, len(self.choices)):
            print(' ' * len(self.choices[i]), end='')
            print(' ', end='')
        print('\r', end='')
    
    def onkeypress(self, key):
        if(key == Key.left):
            self.selected_value = (self.selected_value - 1) if (self.selected_value > 0) else len(self.choices) - 1
            self.update()
        if(key == Key.right):
            self.selected_value = (self.selected_value + 1) % len(self.choices)
            self.update()
        if(key == Key.enter):
            self.listener.stop()

def choice(q:str, a:list[str]) -> tuple[int, str]:
    x = __Choice()
    return x(q, a)

if __name__ == "__main__":
    x = choice('ski?', ['yes', 'no', 'maybe', 'sure', 'y'])

    print(x)