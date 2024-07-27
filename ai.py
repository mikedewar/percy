from openai import OpenAI
import json
import datetime

import todo

class AI():
    def __init__(self) -> None:
        self.client = OpenAI()
        self.model = "gpt-3.5-turbo"

        currentTime = datetime.datetime.now()
        hour = currentTime.hour

        with open('data.json') as f:
            data = json.load(f)
            self.default_questions = "\n".join(data['default_questions'])
            self.qa = data["qa"]
            self.todo_list_prompt = todo.get_todo_list()
            self.meta_prompt = data['meta_prompt']
            # if it's the morning, get the morning prompt
            if hour < 12:
                self.user_prompt = data['morning_prompt']
            # if it's the afternoon, get the afternoon prompt
            else:
                self.user_prompt = data['afternoon_prompt']  
    
        # get the day of the week
        fullNameDayOfWeek = datetime.datetime.now().strftime("%A")
        # get the date formatted in GB standard format
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        # get the current time formatted in GB standard format
        time = datetime.datetime.now().strftime("%H:%M:%S")
        prompt = f"VERY IMPORTANT: Today is {fullNameDayOfWeek} and the date is {date}, the time is {time}. Important: Saturday and Sunday are the weekend for relaxing not working, if the day is Saturday or Sunday make your questions less work related and more time-off chilling related. Your client counts the start of the week and work week as Monday, anything 'new week' related starts on Monday. The end of 'work week' related ends on Friday. IMPORTANT, please don't be asking about the weekend on any other day than Monday or Friday, please pay attention to the current day of the week."
        self.day_date_prompt = prompt

    def get_questions(self) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.up_to_messages()
        )
        
        up_to_questions = response.choices[0].message.content.split("\n")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.todo_messages()
        )

        todo_questions = response.choices[0].message.content.split("\n")


        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.todo_suggestions_messages()
        )

        todo_suggestions_messages = response.choices[0].message.content.split("\n")

        return up_to_questions + todo_questions + todo_suggestions_messages

    
    def get_qa_prompt(self):
        prompt = ""
        for day in self.qa:
            prompt += f"Day: {day}\n"
            for qa in self.qa[day]:
                prompt += f"Question: {qa['q']}\n"
                prompt += f"Answer: {qa['a']}\n"
        return prompt

    def up_to_messages(self) -> list[str]:
        return [
            {"role": "system", "content": self.meta_prompt},
            {"role": "system", "content": self.day_date_prompt},
            {"role": "system", "content": self.default_questions},
            {"role": "system", "content": self.get_qa_prompt()},
            {"role": "user", "content": self.user_prompt}
        ]
    
    def todo_suggestions_messages(self) -> list[str]:
        with open('data.json') as f:
            data = json.load(f)
        return [
            {"role": "system", "content": self.meta_prompt},
            {"role": "system", "content": self.todo_list_prompt},
            {"role": "system", "content": self.get_qa_prompt()},
            {"role": "user", "content": data["suggested_todo_prompt"]}
        ]

    def todo_messages(self) -> str:

        # Load the data from the JSON file
        with open('data.json') as f:
            data = json.load(f)

        todo_prompt = "Here is my current todo list:\n"
        todo_prompt += self.todo_list_prompt

        print(todo_prompt)

        client = OpenAI()
        messages = [
            {"role": "system", "content": data["meta_prompt"]},
            {"role": "system", "content": todo_prompt},
            {"role": "user", "content": data["todo_prompt"]}
        ]
        return messages



    def summarise(self) -> str:

        # Load the data from the JSON file
        with open('data.json') as f:
            data = json.load(f)

        # Initialize an empty dictionary to store the summarized data
        summarized_data = {}

        # Iterate over the data
        qa_prompt = "Here are my notes for the last seven days:\n"
        for day in data["qa"]:
            qa_prompt += "Day: " + day + "\n"
            for x in data["qa"][day]:
                qa_prompt += "Q: " + x['q'] + "\n" + "A: " + x['a'] + "\n"

        # Call the OpenAI API to summarize the data
        client = OpenAI()
        messages = [
            {"role": "system", "content": data["meta_prompt"]},
            {"role": "system", "content": qa_prompt},
            {"role": "user", "content": "please summarise my notes for the last seven days. Please return the summary in .txt format as a bullet pointed list, one bullet point per line. Important: there must be NO numbers at the start of each question! Only return the summary bullets no other text."}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return response.choices[0].message.content;
