from uuid import UUID


class Project:
    def __init__(
        self, project_id: UUID, name: str, description: str, manager_id: UUID
    ):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.manager_id = manager_id
