from django.urls import path
from . import views
from channel_app.api import views as api_views
from . import ajax as a_views

urlpatterns = [
    path('chats', views.chat_index, name='chat_index'),
    path('chatroom/', views.chatroom, name='chatroom'),

    path('ajax-validate-room-name', a_views.validate_room_name, name='validate_room_name'),
    path('ajax-create-group', a_views.ajax_create_group_chat, name='create_group_chat'),
    path('ajax-search-index', a_views.ajax_search_index, name='search_index'),
    # path('ajax-search-room', a_views.ajax_search_room, name='search_chatroom'),
    path('ajax-reload-index', a_views.reload_index_room, name='reload_index_user'),
    # path('conversation/<group_name>/', views.join_group_chat, name='group_chat'),

]
