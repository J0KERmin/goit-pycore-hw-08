from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    def validate_phone(self, phone):
        return len(phone) == 10 and phone.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = self.parse_birthday(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def parse_birthday(self, value):
        day, month, year = map(int, value.split('.'))
        return datetime(year, month, day)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.phones.append(phone)
        else:
            self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        if isinstance(phone, Phone):
            self.phones.remove(phone)
        else:
            self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if old_phone in [p.value for p in self.phones]:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError("Phone number not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name}, phones: {', '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            raise ValueError("Contact not found")

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Contact not found")

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if (next_birthday - today).days <= 7:
                    upcoming_birthdays.append((record.name.value, next_birthday.strftime("%d.%m")))
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name"
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Give me name and phone please."
    return inner

@input_error
def add_contact(args, contacts):
    name, phone = args
    if name not in contacts:
        new_record = Record(name)
        new_record.add_phone(phone)
        contacts.add_record(new_record)
        return f"Contact {name} with phone number {phone} has been added."
    else:
        return f"Contact {name} already exists."


@input_error
def change_contact(args, contacts):
    name, new_phone = args
    if name in contacts.data:
        record = contacts.find(name)
        record.edit_phone(new_phone)
        return f"Phone number for {name} has been changed to {new_phone}."
    else:
        return f"Contact {name} not found."


@input_error
def show_phone(args, contacts):
    name = args[0]
    if name in contacts.data:
        record = contacts.find(name)
        return f"Phone number for {name} is {record.phones[0]}."
    else:
        return f"Contact {name} not found."


@input_error
def show_all_contacts(args, contacts):
    if not contacts:
        return "Phone book is empty."
    else:
        return "\n".join([str(record) for record in contacts.data.values()])


@input_error
def search_contact(args, contacts):
    name = args[0]
    if name in contacts.data:
        record = contacts.find(name)
        return f"Phone number for {name} is {record.phones[0]}."
    else:
        return f"No contact with the name {name} found."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record.birthday:
        return f"{name}'s birthday is on {record.birthday}."
    else:
        return f"{name} does not have a birthday set."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{name} has a birthday on {date}" for name, date in upcoming_birthdays])
    else:
        return "No upcoming birthdays within the next week."


@input_error
def parse_input(input_str):
    tokens = input_str.strip().split()
    command = tokens[0].lower()
    args = tokens[1:]
    return command, args


@input_error
def add_contact(args, contacts):
    name, phone = args
    if name not in contacts.data:
        new_record = Record(name)
        new_record.add_phone(phone)
        contacts.add_record(new_record)
        return f"Contact {name} with phone number {phone} has been added."
    else:
        return f"Contact {name} already exists."


def show_commands():
    return "Available commands:\n" \
           "add <name> <phone_number>: Add a new contact with the given name and phone number.\n" \
           "change <name> <new_phone_number>: Change the phone number for the contact with the given name.\n" \
           "phone <name>: Show the phone number for the contact with the given name.\n" \
           "search <name>: Search for a contact by name.\n" \
           "all: Show all contacts.\n" \
           "add-birthday <name> <birthday>: Add a birthday for the contact with the given name.\n" \
           "show-birthday <name>: Show the birthday for the contact with the given name.\n" \
           "birthdays: Show upcoming birthdays for the next week.\n" \
           "close or exit: Exit the program."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    phone_book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter command: ")
        command, args = parse_input(user_input)
        if command == "add":
            print(add_contact(args, phone_book))
        elif command == "change":
            print(change_contact(args, phone_book))
        elif command == "phone":
            print(show_phone(args, phone_book))
        elif command == "search":
            print(search_contact(args, phone_book))
        elif command == "all":
            print(show_all_contacts(args, phone_book))
        elif command == "add-birthday":
            print(add_birthday(args, phone_book))
        elif command == "show-birthday":
            print(show_birthday(args, phone_book))
        elif command == "birthdays":
            print(birthdays(args, phone_book))
        elif command == "exit" or command == "close":
            save_data(phone_book)
            print("Goodbye!")
            break
        else:
            print("Invalid command. Type 'commands' for a list of available commands.")

if __name__ == "__main__":
    main()


