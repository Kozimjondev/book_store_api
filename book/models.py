from django.db import models
from django.db.models import When, Case
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.template.defaultfilters import slugify
from rest_framework.exceptions import ValidationError
from user.models import CustomUser


class Category(models.Model):
    name = models.CharField("Category", max_length=100)
    url = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)


class Book(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='images/%Y/%m/%d/', default='default.png')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=200)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='owner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, related_name='category')
    readers = models.ManyToManyField(CustomUser, through='UserBookRelation', related_name='readers')
    # count_book = models.PositiveIntegerField(editable=False, default=0)
    collected_money = models.DecimalField(default=0, decimal_places=2, max_digits=19, editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.url)])

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.name)
        return super(Book, self).save(*args, **kwargs)


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    # buy = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}: {self.book}, rate: {self.rate}"


class UserBuyBook(models.Model):
    is_bought = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def name(self):
        return f"{self.user} bought {self.book.name}"


@receiver(pre_save, sender=UserBuyBook)
def book_buy(sender, instance, **kwargs):
    # not_liked = UserBuyBook.objects.annotate(Case(When(is_bought=False, then=True)))
    # is_liked = UserBuyBook.objects.annotate(Case(When(is_bought=True, then=True)))
    if not instance.pk:
        if instance.is_bought == False:
            if instance.user.money >= instance.book.price:
                instance.is_bought = True
                # print(instance.user.money)
                # print(instance.book.price)
                instance.book.collected_money += instance.book.price
                # print(instance.book.collected_money)
                instance.book.save()
                instance.user.money -= instance.book.price
                # print(instance.user.money)
                instance.user.save()
            else:
                raise ValidationError("You don't have enough money to buy this book!")
        else:
            raise ValidationError("You have already bought this book!")

