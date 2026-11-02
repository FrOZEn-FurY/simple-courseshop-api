from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .serializers import HomeSerializer, CategorySerializer, PostSerializer, CommentSerializer
from .models import Post, Category, UserFavorite

from utils.functions import get_response


class HomeView(ListAPIView):
    serializer_class = HomeSerializer
    queryset = Post.objects.all()
    pagination_class = PageNumberPagination


class CategoryView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent=None)


class CategoryPostView(ListAPIView):
    serializer_class = HomeSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Post.objects.filter(category__slug=self.kwargs['slug'])


class PostDetailView(RetrieveAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_object(self):
        post = get_object_or_404(self.queryset, category__slug=self.kwargs['slug'], pk=self.kwargs['pk'])
        return post


class AddToFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        try:
            favorite = UserFavorite.objects.get(post=post, user=request.user)
            favorite.delete()
            return get_response(
                    status=status.HTTP_204_NO_CONTENT,
                    message="Removed from favorites successfully."
                )
        except ObjectDoesNotExist:
            UserFavorite.objects.create(post=post, user=request.user)
            return get_response(
                    status=status.HTTP_201_CREATED,
                    message="Added to favorites successfully."
                )


class AddComment(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data['author'] = request.user.pk
        request.data['post'] = self.kwargs['post_pk']
        return super().post(request, *args, **kwargs)