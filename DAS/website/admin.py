from django.contrib import admin
from django.contrib import admin
from django.db.models import Count
from django.urls import path
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .models import ScannedData, Profile



# Register your models here.
admin.site.register(Profile)
admin.site.register(ScannedData)
