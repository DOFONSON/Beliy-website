import graphene
from graphene_django import DjangoObjectType
from .models import LiteraryWork

class LiteraryWorkType(DjangoObjectType):
    class Meta:
        model = LiteraryWork

class Query(graphene.ObjectType):
    all_works = graphene.List(LiteraryWorkType)

    def resolve_all_works(root, info):
        return LiteraryWork.objects.all()

schema = graphene.Schema(query=Query)