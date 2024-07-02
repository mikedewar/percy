from cmd import Cmd
from ai import AI
import datetime
import json


class Percy(Cmd):


    prompt = ' > '

    def __init__(self) -> None:
        super().__init__()
        
        self.ai = AI()

        currentTime = datetime.datetime.now()
        hour = currentTime.hour

        self.time_of_day = "morning" if hour < 12 else "afternoon"

        self.questions = self.ai.get_questions()
        self.answers = []

    def preloop(self):
        print("🐶", self.questions[0])
        

    def default(self, inp):
        if inp:
            self.answers.append({"q": self.questions[len(self.answers)], "a": inp})
            if len(self.answers) < len(self.questions):
                print("🐶", self.questions[len(self.answers)])
            else:
                print('🐶 Goodbye!')
                return True

    def do_EOF(self, inp):
        return True
    
    def update_qas(self):

        today = datetime.datetime.now().strftime("%A")

        with open('data.json', 'r') as f:
            data = json.load(f)
            data['qa'][today + "_" + self.time_of_day] = [qa for qa in self.answers]
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    percy = Percy()
    percy.cmdloop()
    percy.update_qas()

    print("🐶 here is the summary of the last 7 days")
    print(percy.ai.summarise())

