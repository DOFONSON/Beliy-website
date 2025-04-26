import graphene
from graphene_django import DjangoObjectType
from .models import Article, ArticleRating

class ArticleRatingType(DjangoObjectType):
    class Meta:
        model = ArticleRating
        fields = ('value', 'user', 'created_at')

class ArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = ('id', 'title', 'slug', 'content', 'image', 'created_at', 'updated_at', 'ratings')

    average_rating = graphene.Float()
    rating_count = graphene.Int()

    def resolve_average_rating(self, info):
        return self.get_average_rating()

    def resolve_rating_count(self, info):
        return self.get_rating_count()

class Query(graphene.ObjectType):
    all_articles = graphene.List(ArticleType)
    article = graphene.Field(ArticleType, id=graphene.Int(), slug=graphene.String())

    def resolve_all_articles(self, info):
        return Article.objects.all()

    def resolve_article(self, info, id=None, slug=None):
        if id:
            return Article.objects.get(pk=id)
        if slug:
            return Article.objects.get(slug=slug)
        return None

class RateArticle(graphene.Mutation):
    class Arguments:
        article_id = graphene.Int(required=True)
        value = graphene.Int(required=True)

    success = graphene.Boolean()
    average_rating = graphene.Float()
    rating_count = graphene.Int()

    @classmethod
    def mutate(cls, root, info, article_id, value):
        if not info.context.user.is_authenticated:
            raise Exception("Необходима авторизация")
        
        article = Article.objects.get(pk=article_id)
        rating, created = ArticleRating.objects.update_or_create(
            article=article,
            user=info.context.user,
            defaults={'value': value}
        )
        
        return RateArticle(
            success=True,
            average_rating=article.get_average_rating(),
            rating_count=article.get_rating_count()
        )

class Mutation(graphene.ObjectType):
    rate_article = RateArticle.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)