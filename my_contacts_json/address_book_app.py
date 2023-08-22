import json
import datetime
from collections import UserDict

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        self.__value = value

class Name(Field):
    
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        if len(value) < 2:
            raise ValueError("Імʼя повинно бути довше ніж 2 символи")
        self.__value = value

class Phone(Field):
    
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        if not all(char.isdigit() for char in value):
            raise ValueError("Номер телефону повинен складатися лише з цифр")
        self.__value = value

class Birthday(Field):
    
    @property
    def value(self) -> datetime.date:
        return self.__value

    @value.setter
    def value(self, value) -> None:
        if not isinstance(value, datetime.date):
            raise ValueError("День народження повинен бути об'єктом datetime.date")
        self.__value = value

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.optional_fields = {}
        if phone:
            self.add_phone(phone)
        if birthday:
            self.add_birthday(birthday)

    def add_field(self, field):
        if isinstance(field, Field):
            self.optional_fields[field.name] = field

    def remove_field(self, field_name):
        if field_name in self.optional_fields:
            del self.optional_fields[field_name]

    def edit_field(self, field_name, new_value):
        if field_name in self.optional_fields:
            self.optional_fields[field_name].value = new_value

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.optional_fields['Телефон'] = phone

    def add_birthday(self, birthday):
        if isinstance(birthday, Birthday):
            self.optional_fields['День народження'] = birthday

    def days_to_birthday(self):
        if 'День народження' in self.optional_fields and self.optional_fields['День народження'].value:
            today = datetime.date.today()
            birthday = self.optional_fields['День народження'].value 
            next_birthday = datetime.date(today.year, birthday.month, birthday.day)
            if today > next_birthday:
                next_birthday = datetime.date(today.year + 1, birthday.month, birthday.day)
            days_remaining = (next_birthday - today).days
            return days_remaining

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def save_to_file(self, filename):
        with open(filename, 'w', encoding="utf-8") as file:
            data = {'contacts': self.data}
            json.dump(data, file, default=self.serialize_contact, ensure_ascii=False, indent=4)


    def serialize_contact(self, obj):
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y %m %d')
        return obj.__dict__
    
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                data = json.load(file)
            self.data = data['contacts']
        except FileNotFoundError:
            self.data = {}
        except UnicodeDecodeError:
            print(f"Error decoding file '{filename}' with UTF-8 encoding. Trying different encodings...")
        encodings_to_try = ["utf-16", "cp1251", "latin-1"]
        for encoding in encodings_to_try:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    data = json.load(file)
                    self.data = data['contacts']
                    print(f"File successfully decoded using encoding: {encoding}")
                    break
            except UnicodeDecodeError:
                print(f"Failed to decode file using encoding: {encoding}")

    def search(self, query):
        query = query.lower()  # Перетворимо запит на нижній регістр для порівняння

        results = []

        for contact in self.data.values():
            contact_name = contact.name.value.lower()
            contact_phone = contact.optional_fields.get('Телефон', None)
            if contact_phone:
                contact_phone = contact_phone.value.lower()

            if query in contact_name or (contact_phone and query in contact_phone):
                results.append(contact)


if __name__ == "__main__":
    ab = AddressBook()
    try:
        ab.load_from_file('my_contacts.json')
    except FileNotFoundError:
        pass


    while True:
        print("1. Додати контакт")
        print("2. Пошук контакту")
        print("3. Вийти")
        choice = input("Оберіть дію: ")

        if choice == '1':
            name_value = input("Введіть ім'я: ")
            phone_value = input("Введіть номер телефону: ")
            birthday_value = input("Введіть день народження (рррр-мм-дд): ")
            birthday_date = datetime.datetime.strptime(birthday_value, '%Y-%m-%d').date()

            name = Name(name_value)
            phone = Phone(phone_value)
            birthday = Birthday(birthday_date)
            rec = Record(name, phone=phone, birthday=birthday)
            ab.add_record(rec)
            ab.save_to_file('my_contacts.json')
            print("Контакт успішно доданий та збережений.")

        elif choice == '2':
            search_query = input("Введіть пошуковий запит: ")
            search_results = ab.search(search_query)

            if search_results:
                print("Результати пошуку:")
                for contact in search_results:
                    print(contact.name.value)
            else:
                print("Результати не знайдені.")

        elif choice == '3':
            break

        else:
            print("Невірний вибір. Спробуйте знову.")

    print("Програма завершена.")



