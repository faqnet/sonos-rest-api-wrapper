class Favourite:

    def __init__ (self, id, name, description, image_url, service=None):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.image_url: str = image_url
        self.service: str = service
