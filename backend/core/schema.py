import graphene
from works.schema import Query as WorksQuery

class Query(WorksQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query) 