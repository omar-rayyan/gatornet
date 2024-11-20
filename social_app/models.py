from django.db import models
from users_app.models import User

class PostsManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        if len(postData['content']) < 1:
            errors["content"] = "You cannot publish an empty post."
            return errors
        return errors
    def delete_post(self, post_id):
        post = Post.objects.get(id=post_id)
        post.delete()
    def update_post(self, data):
        post = Post.objects.get(id=data['post_id'])
        post.content = data['content']
        post.save()
    def create_post(self, data):
        return Post.objects.create(content=data['content'], creator=data['creator'], shared=data['shared'], shared_post_id=data['shared_post_id'])
    def get_user_posts(self, user_id):
        user = User.objects.get(id=user_id)
        return Post.objects.filter(creator=user)
    def get_friends_posts(self, user_id):
        user = User.objects.get(id=user_id)
        friends = user.friends()
        return Post.objects.filter(creator__in=friends)
    def get_post_comments(self, post_id):
        post = Post.objects.get(id=post_id)
        return post.comments
    def get_post_comments_count(self, post_id):
        post = Post.objects.get(id=post_id)
        return post.comments.count()

class CommentManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        if len(postData['content']) < 1:
            errors["content"] = "You cannot post an empty comment."
            return errors
        return errors
    def delete_comment(self, comment_id):
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
    def update_comment(self, data):
        comment = Comment.objects.get(id=data['comment_id'])
        comment.content = data['content']
        comment.save()
    def create_comment(self, data):
        return Comment.objects.create(content=data['content'], user=data['user'], post=data['post'])

class FriendshipManager(models.Manager):
    def create_friendship(self, data):
        return Friendship.objects.create(friend_1=data['friend_1'], friend_2=data['friend_2'])
    def remove_friendship(self, data):
        user_1 = User.objects.get(id=data['user_1'])
        friendship_1 = Friendship.objects.get(friend_1=user_1)
        if friendship_1:
            friendship_1.delete()
        else:
            friendship_2 = Friendship.objects.get(friend_2=user_1)
            friendship_2.delete()

class LikeManager(models.Manager):
    def add_like(self, data):
        post = Post.objects.get(id=data['post_id'])
        return Like.objects.create(user=data['user'], post=post)
    def remove_like(self, data):
        user = User.objects.get(id=data['user_id'])
        post = Post.objects.get(id=data['post_id'])
        like = Like.objects.get(user=user, post=post)
        like.delete()
    def get_likes_count(self, post_id):
        post = Post.objects.get(id=post_id)
        return post.likes.count()
    def has_user_liked_post(self, data):
        user = User.objects.get(id=data['user_id'])
        post = Post.objects.get(id=data['post_id'])
        like = Like.objects.get(user=user, post=post)
        return True if like else False

class PersonalDetailsManager(models.Manager):
    def create_personal_details_record(self, user):
        PersonalDetails.objects.create(user=user, bio='', location='', workplace='', phone_number='', relationship_status='')
    def update_personal_details_record(self, data):
        record = PersonalDetails.objects.get(user=data['user'])
        if data['bio']:
            record.bio = data['bio']
        if data['location']:
            record.location = data['location']
        if data['workplace']:
            record.workplace = data['workplace']
        if data['phone_number']:
            record.phone_number = data['phone_number']
        if data['relationship_status']:
            record.relationship_status = data['relationship_status']
        record.save()
        
class MessageManager(models.Manager):
    def send_message(self, data):
        sender = User.objects.get(id=data['sender_id'])
        recipient = User.objects.get(id=data['recipient_id'])
        Message.objects.create(sender=sender, recipient=recipient, content=data['content'])
    def get_messages(self, data):
        user = User.objects.get(id=data['user_id'])
        friend = User.objects.get(id=data['friend_id'])
        messages = Message.objects.filter(models.Q(sender=user, recipient=friend) | models.Q(sender=friend, recipient=user)).order_by('created_at')
        messages_dictionary = [
            {
                "sender": message.sender.id,
                "recipient": message.recipient.id,
                "content": message.content,
            }
            for message in messages
        ]
        return messages_dictionary
    
class Post(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(User, related_name = "all_posts", on_delete = models.CASCADE)
    shared = models.BooleanField(default=False)
    shared_post_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostsManager()

class Comment(models.Model):
    content = models.TextField()
    commentor = models.ForeignKey(User, related_name = "posted_comments", on_delete = models.CASCADE)
    post = models.ForeignKey(Post, related_name = "comments", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CommentManager()

class Like(models.Model):
    user = models.ForeignKey(User, related_name = "liked_posts", on_delete = models.CASCADE)
    post = models.ForeignKey(Post, related_name = "likes", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = LikeManager()

class Friendship(models.Model):
    friend_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_initiated")
    friend_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_received")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = FriendshipManager()

class PersonalDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_details")
    bio = models.TextField()
    location = models.TextField()
    workplace = models.TextField()
    phone_number = models.TextField()
    relationship_status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PersonalDetailsManager()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MessageManager()