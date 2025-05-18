from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
import calendar
import random
import json

# Хранение состояния
class DataStorage:
    def __init__(self):
        self.supports: list['Support'] = []
        self.clients: list['Client'] = []
        self.chats: list['Chat'] = []

    def AddChat(self, chat: 'Chat'):
        """
        Добавление нового чата
        """
        self.chats.append(chat)

    def AddClient(self, client: 'Client'):
        """
        Добавление нового клиента
        """
        self.clients.append(client)

    def AddSupport(self, support: 'Support'):
        """
        Добавление нового оператора
        """
        self.supports.append(support)

    def GetAvailableSupport(self) -> Optional['Support']:
        """
        Получение доступного оператора
        """
        available = [s for s in self.supports if s.isAvailable]
        return random.choice(available) if available else None

    def ExportJson(self, filename: str):
        """
        Выгрузка в JSON
        """
        data = {
            "supports": [s.ToDict() for s in self.supports],
            "clients": [c.ToDict() for c in self.clients],
            "chats": [chat.ToDict() for chat in self.chats]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, default = str, indent = 2)
        print(json.dumps(data, indent = 2))

    def GetChatsByUser(self, userId: str) -> List['Chat']:
        """
        Возвращает чаты ассоциированные с конкретным пользователем (Support || Client)
        """
        return [chat for chat in self.chats
                if chat.clientId == userId or userId is chat.supportIds]

# Базовый класс для сущностей Support и Client
@dataclass
class Person:
    fullname: str
    city: str
    dob: datetime
    exp: int
    id: str = field(default_factory=lambda: str(uuid4()))
    currentChat: Optional['Chat'] = None

    def SendMessage(self, text: str):
        """
        Отправка сообщения в чат
        """
        if self.currentChat is not None:
            newMessage = Message(text, self.id)
            self.currentChat.AddMessage(newMessage)

    def ToDict(self):
        """
        Возвращает словарь из экземпляра объекта
        """
        return {
            "id": self.id,
            "fullname": self.fullname,
            "city": self.city,
            "dob": self.dob.isoformat(),
            "exp": self.exp,
            "currentChat": self.currentChat.id if self.currentChat else None
        }

# Оператор
@dataclass
class Support(Person):
    post: str = "L1"
    isAvailable: bool = True

    def CloseChat(self):
        """
        Закрывает чат, что-то из разряда 'выполнить'
        """
        if self.currentChat and not self.currentChat.isActive:
            raise ValueError("chat already closed")

        self.currentChat.Close()
        self.isAvailable = True
        self.currentChat = None

    def ToDict(self):
        """
        Возвращает словарь из экземпляра объекта
        """
        data = super().ToDict()
        data.update({
            "post": self.post,
            "isAvailable": self.isAvailable
        })
        return data

# Клиент с возможностью открыть обращение
@dataclass
class Client(Person):
    messageTemplates = ("Hello", "Missing item", "Wrong order delivered",
                        "Where is my order", "Wrong item")
 
    def InitChat(self, data: DataStorage):
        """
        Возможность 'открыть' обращение
        """
        support = data.GetAvailableSupport()
        if not support:
            raise ValueError("no available supports")

        chat = Chat(clientId = self.id)
        chat.supportIds.append(support.id)

        self.currentChat = chat
        support.currentChat = chat
        support.isAvailable = False

        data.AddChat(chat)

        return chat
    
    def SetCsat(self, csat: int):
        """
        Установка ксата и проверка его на валидность
        """
        if self.currentChat and not self.currentChat.isActive:
            if 1 <= csat <= 5:
                self.currentChat.csat = csat
            else:
                raise ValueError("CSAT must be 1-5")

@dataclass    
class Message:
    text: str
    senderId:str
    sendTime: datetime = field(default_factory=datetime.now)

    def ToDict(self):
        """
        Возвращает словарь из экземпляра объекта
        """
        return {
            "text": self.text,
            "senderId": self.senderId,
            "sendTime": self.sendTime.isoformat()
        }

@dataclass      
class Chat:
    clientId: str
    id: str = field(default_factory=lambda: str(uuid4()))
    initTime: datetime = field(default_factory=datetime.now)
    supportIds: List[str] = field(default_factory=list)
    isActive: bool = True
    csat: Optional[int] = None
    messages: List[Message] = field(default_factory=list)

    def AddMessage(self, message: 'Message'):
        """
        Добавляет сообщение в чат
        """
        self.messages.append(message)

    def Close(self):
        """
        Закрывает чат
        """
        self.isActive = False

    def ToDict(self):
        """
        Возвращает словарь из экземпляра объекта
        """
        return {
            "id": self.id,
            "clientId": self.clientId,
            "supportIds": self.supportIds,
            "initTime": self.initTime.isoformat(),
            "isActive": self.isActive,
            "csat": self.csat,
            "messages": [m.ToDict() for m in self.messages]
        }
    
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
        self.person = {}

    def _GenerateFullname(self):
        """
        Генерация 'случайных' имён
        """
        name = random.choice(self.NAMES)
        patron = random.choice(self.PATRONS)
        surname = random.choice(self.SURNAMES)
        self.person['fullname'] = f"{surname} {name} {patron}"
  
    def _GenerateCity(self):
        """
        Выбор города из объявленного ранее кортежа
        """
        self.person['city'] = random.choice(self.CITIES)

    def _GenerateDob(self):
        """
        Генерация даты рождения с учётом високосных
        """
        month = random.randint(1, 12)
        year = random.randint(1960, 2010)
        # Получаем количество дней в месяце по григорианскому включая високосные
        maxDays = calendar.monthrange(year, month)[1] # 0 - день недели, 1 - количество дней в месяце
        day = random.randint(1, maxDays)
        dob = datetime(year, month, day)
        self.person['dob'] = dob

    def _GenerateExp(self):
        """
        Генерирует стаж для Support и время с момента регистрации для Client.
        Значение в месяцах
        """
        self.person['exp'] = random.randint(1, 120)

class SupportBuilder(PersonBuilder):
    POSTS = ("L1", "L2", "L3", "TL", "QA")

    def Build(self) -> Support:
        """
        Собирает и возвращает готовый объект класса Support
        """
        self._GenerateFullname()
        self._GenerateCity()
        self._GenerateDob()
        self._GenerateExp()
        return Support(
            fullname = self.person['fullname'],
            city = self.person['city'],
            dob = self.person['dob'],
            exp = self.person['exp'],
            post = random.choice(self.POSTS)
        )

class ClientBuilder(PersonBuilder):
    def Build(self) -> Client:
        """
        Собирает и возвращает готовый объект класса Client
        """
        self._GenerateFullname()
        self._GenerateCity()
        self._GenerateDob()
        self._GenerateExp()
        return Client(
            fullname = self.person['fullname'],
            city = self.person['city'],
            dob = self.person['dob'],
            exp = self.person['exp']
        )

class Platform:
    def __init__(self, clientsCount, supportsCount):
        self.data = DataStorage()
        self._GenerateUsers(clientsCount, supportsCount)

    def _GenerateUsers(self, clientsCount: int, supportsCount: int):
        """
        Создаёт клиентов и операторов в необходимом диапазоне
        """
        for _ in range(clientsCount):
            self.data.AddClient(ClientBuilder().Build())

        for _ in range(supportsCount):
            self.data.AddSupport(SupportBuilder().Build())

    def StartChats(self, chatCount):
        """
        Инициализирует начальные обращения
        """
        clients = random.sample(self.data.clients, chatCount)
        for client in clients:
            try:
                chat = client.InitChat(self.data)
                client.SendMessage(random.choice(client.messageTemplates))
            except ValueError as e:
                print(f"error starting chat: {e}")

    def Start(self):
        """
        Запускает симуляцию платформы
        """
        for chat in self.data.chats:
            if chat.isActive and random.random() < 0.3:
                support = next(s for s in self.data.supports 
                               if s.id in chat.supportIds)
                support.CloseChat()
                if random.random() < 0.7:
                    client = next(c for c in self.data.clients
                                  if c.id == chat.clientId)
                    client.SetCsat(random.randint(1, 5))