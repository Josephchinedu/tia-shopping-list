from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q


# Create your models here.
class ShoppingList(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SHOPPING LIST"
        verbose_name_plural = "SHOPPING LISTS"

    @classmethod
    def create_shopping_list(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def get_shopping_list(cls, user_id):
        return cls.objects.filter(user__id=user_id, is_deleted=False)

    @classmethod
    def get_shopping_list_by_id(cls, user_id, id):
        return cls.objects.filter(user__id=user_id, id=id, is_deleted=False).first()

    @classmethod
    def get_shopping_list_by_name(cls, user_id, name):
        return cls.objects.filter(user__id=user_id, name=name, is_deleted=False).first()

    @classmethod
    def search_shopping_list(cls, user_id, search):
        return cls.objects.filter(
            Q(user__id=user_id) & Q(name__icontains=search) & Q(is_deleted=False)
        )

    @classmethod
    def sort_data(cls, queryset, sort_by):
        if sort_by == "asc":
            return queryset.order_by("id")
        elif sort_by == "desc":
            return queryset.order_by("-id")

        return queryset

    @classmethod
    def filter_by_date(cls, start_date, end_date, user_id):
        return cls.objects.filter(
            Q(user__id=user_id)
            & Q(created_at__range=[start_date, end_date])
            & Q(is_deleted=False)
        )
