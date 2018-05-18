from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField

from hc.lib import emails

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class Blog(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    body = RichTextField()
    author = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return('view_blog_post', None, {'slug':self.slug})

class Comment(models.Model):
    blog = models.ForeignKey(Blog)
    name = models.ForeignKey(User)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body

# Create your models here.
class FrequentlyAskedQuestion(models.Model):
    CHOICES = {
        ('s','showing'),
        ('h','hidden')
    }
    question = models.TextField(help_text='Enter any question')
    answer = models.TextField(blank=True,null=True)
    email = models.EmailField(help_text='Enter your email')
    status = models.CharField(choices=CHOICES,max_length=1,default='h')

class EmailTasks(models.Model):
    owner = models.ForeignKey(User)
    task_name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=100)
    recipients = models.CharField(max_length=200)
    message = models.TextField()
    interval =models.CharField(max_length=100)
    time = models.IntegerField()

    def __str__(self):
        return self.task_name
