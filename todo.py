import todotxt

def get_todo_list() -> str:
    tasks = todotxt.Tasks("/Users/mikedewar/todo/todo.txt")
    tasks.load()
    return "\n".join([str(task) for task in tasks.tasks])