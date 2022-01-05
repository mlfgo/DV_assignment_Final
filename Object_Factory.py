from abc import ABC
from abc import abstractmethod
import io

class Entity_Method(ABC):
    @abstractmethod
    def invoke(self):
        pass

'''
A factory object 
'''
class Object_Factory:
    def __init__(self,entity_name=None,entity=None):
        self.entity_name=entity_name
        self.entity=entity
        self.dfs = {}
        if not entity_name or not entity:
            self.dfs[entity_name] = entity

    def getFactory(self):
        return self

    def add_data_entity(self,entity_name,entity):
        self.entity_name = entity_name
        self.entity = entity
        self.dfs[entity_name]=entity

    def inokce_method(self,method):
        method.invoke()

    def __str__(self):
        f=io.StringIO()
        for i in range(len(self.entity.index)):
            f.write(str(self.entity.iloc[i,2])+"\n")
        return f.getvalue()
