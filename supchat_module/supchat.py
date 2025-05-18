from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
import random
import calendar

# Хранение состояния
class DataStorage:
    def __init__(self):
        self.supports: list[Support] = []
        self.clients: list[Client] = []
        self.chats: list[Chat] = []

    def AddChat(self, chat: 'Chat'):
        self.chats.append(chat)

    def AddClient(self, client: 'Client'):
        self.clients.append(client)

    def AddSupport(self, support: 'Support'):
        self.supports.append(support)

# Базовый класс для сущностей Support и Client
@dataclass
class Person:
    fullname: str
    city: str
    dob: datetime
    exp: int
    id: str = None
    currentChatId: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())

    def SendMessage(self, text):
        if self.currentChat is not None:
            newMessage = Message(text, self.id)

# Оператор
# Добавляется должность и доступность
@dataclass
class Support(Person):
    post: str = "L1"
    isAvailable: bool = True

# Клиент с возможностью открыть обращение
class Client(Person):
    messageTemplates = ("Hello", "Missing item", "Wrong order delivered",
                        "Where is my order", "Wrong item")
 
    def InitChat(self, data: DataStorage) -> str:
        newChat = Chat(clientId = self.id)
        data.AddChat(newChat)
        return newChat.id
    

# Решил использовать строителя для генерации сущностей
# Заполняет объект псевдослучайными значениями
class PersonBuilder:
    # Кортежи для неизменяемости исходных значений
    CITIES = ("Novosibirsk", "Moskva", "Kazan", "Ufa",
              "Sochi", "Peterburg", "Omsk", "Tomsk")
    NAMES = ("Alexey", "Vladimir", "Dmitriy", "Makar", 
             "Lev", "Vadim", "Danil", "Arkadiy", "Dennis")
    PATRONS = ("Alekseevich", "Vladimirovich", "Dmitrievich", 
               "Vadimovich", "Sergeevich", "Konstantinovich", 
               "Mihailovich", "Aleksandrovich", "Vadimovich")
    SURNAMES = ("Kazakov", "Tyan", "Nichkov", "Samoilov", "Bezrukov",
                "Lenin", "Ritchie", "Kochin", "Tokarev")

    def __init__(self):
        self.person = Person(
            fullname = None,
            city = None,
            dob = None,
            exp = None
        )

    def GenerateFullname(self):
        """
        Генерация 'случайных' имён
        """
        name = random.choice(self.NAMES)
        patron = random.choice(self.PATRONS)
        surname = random.choice(self.SURNAMES)
        self.person.fullname = f"{surname} {name} {patron}"
  
    def GenerateCity(self):
        """
        Выбор города из объявленного ранее кортежа
        """
        self.person.city = random.choice(self.CITIES)

    def GenerateDob(self):
        """
        Генерация даты рождения с учётом високосных
        """
        month = random.randint(1, 12)
        year = random.randint(1960, 2010)
        # Получаем количество дней в месяце по григорианскому включая високосные
        maxDays = calendar.monthrange(year, month)[1] # 0 - день недели, 1 - количество дней в месяце
        day = random.randint(1, maxDays)
        dob = datetime(year, month, day)
        self.person.dob = dob

    def _generateCommon(self):
        """
        Выполняет общую инициализацию
        """
        self.GenerateFullname()
        self.GenerateCity()
        self.GenerateDob()

# Сущность оператора
class SupportBuilder(PersonBuilder):
    POSTS = ["L1", "L2", "L3", "TL", "QA"]

    def Build(self) -> Support:
        """
        Собирает и возвращает готовый объект класса
        """
        self.person = Support(
            fullname = None,
            city = None,
            dob = None,
            exp = random.randint(1, 120), # Опыт сотрудника в месяцах
            post = random.choice(self.POSTS),
            isAvailable = True
        )
        self._generateCommon()
        return self.person

class ClientBuilder(PersonBuilder):
    """
    Собирает и возвращает готовый объект класса
    """
    def Build(self) -> Client:
        self.person = Client(
        fullname = None,
        city = None,
        dob = None,
        exp = random.randint(1, 120) # Дата с момента регистрации клиента тоже в месяцах
        )
        self._generateCommon()
        return self.person

class Message:
    def __init__(self, text, id):
        self.text = text
        self.sendTime = datetime.now()
        self.senderId = id

@dataclass
class Chat:
    id: str = str(uuid4())
    clientId: str = None
    initTime: datetime = datetime.now()
    supportsIds: list[str] = None
    isActive: bool = True
    csat: int = None
    messages: list[Message] = None

    def __post_init__(self):
        if self.supportsIds is None:
            self.supportsIds = []
        if self.csat and not (1 <= self.csat <= 5):
            raise ValueError("invalid csat value")

class Platform:
    data = DataStorage()

    def __init__(self, clientsCount, supportsCount):
        spBuilder = SupportBuilder()
        clBuilder = ClientBuilder()

        for i in range(1, supportsCount):
            newSupport = spBuilder.Build()
            self.data.AddSupport(newSupport)

        for i in range(1, clientsCount):
            newClient = clBuilder.Build()
            self.data.AddClient(newClient)

    def startChats(self, chatCount):
        if chatCount >= len(self.data.clients):
            raise ValueError('chats count cant be more than clients count')
        for i in self.data.clients:
            i.currentChatId = i.InitChat()
            message = random.choice(i.messageTemplates)
            i.SendMessage(message)

platform = Platform(20, 10)
