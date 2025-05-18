from supchat import Platform

if __name__ == "__main__":
    platform = Platform(100, 20)
    platform.StartChats(50)
    platform.Start()
    platform.data.ExportJson("data.json")