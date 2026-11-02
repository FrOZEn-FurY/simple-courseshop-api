from rest_framework import serializers

from .models import Post, Category, PostData, Comment


class HomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug', 'children')


CategorySerializer._declared_fields['children'] = CategorySerializer(
    many=True,
    source='get_children'
)

class PostDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostData
        exclude = ('post',)


class PostSerializer(serializers.ModelSerializer):
    post_data = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_post_data(self, obj):
        data = PostData.objects.filter(post=obj)
        data_serialized = PostDataSerializer(many=True).to_representation(data)
        return data_serialized

    def get_comments(self, obj):
        comments = Comment.objects.filter(post=obj)
        comments_serialized = CommentSerializer(many=True).to_representation(comments)
        return comments_serialized


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"