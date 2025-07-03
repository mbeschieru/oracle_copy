from uuid import UUID

class Project:
    def __init__(self, project_id: UUID, name: str, description: str):
        self.project_id = project_id
        self.name = name
        self.description = description
