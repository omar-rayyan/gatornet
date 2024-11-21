from django.shortcuts import render, redirect
from social_app.models import *
from django.contrib import messages

def root(request):
    return redirect('home')
def home(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    context = {
        'posts': User.objects.get_friends_posts(int(request.session['user_id']))
    }
    return render(request, 'home.html', context)
def home_dev(request):

    return render(request, 'home.html')
def view_post(request, id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    post = Post.objects.get_post(id)
    context = {
        'post': post,
        'comments': post.comments,
        'comments_count': post.comments.count(),
        'likes': post.likes,
        'likes_count': post.likes.count(),
        'has_user_liked_post': Post.objects.has_user_liked_post(id, int(request.session['user_id']))
    }
    return render(request, 'view_post.html', context)

def view_profile(request, id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user = User.objects.get_user(id)
    context = {
        'user': user,
        'posts': user.posts,
        'posts_count': user.posts.count(),
        'friends': user.friends,
        'friends_count': user.friends.count(),
        'personal_details': user.personal_details,
    }
    return render(request, 'view_profile.html', context)

def like_post(request):
    if request.method == 'POST':
        post_id = request.POST['post_id']
        user_id = request.session['user_id']
        if not post_id or not user_id:
            return redirect('home')
        post = Post.objects.get_post(post_id)
        user = User.objects.get_user(user_id)
        if post.likes.filter(user=user).exists():
            Like.objects.remove_like(post_id, user_id)
        else:
            Like.objects.add_like(post_id, user_id)
        redirect_target = 'view_post' if request.POST['current_view'] == 'view_post' else 'home'
        return redirect(redirect_target, id=post_id) if redirect_target == 'view_post' else redirect(redirect_target)
    return redirect('home')

def create_post(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        errors = Post.objects.basic_validator(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='create_post')
            redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
            profile_id = int(request.POST['current_profile'])
            return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
        user_id = request.session['user_id']
        user = User.objects.get_user(user_id)
        Post.objects.create_post({'content': request.POST['content'], 'creator': user, 'shared': False, 'shared_post_id': 0})
        redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
        profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    return redirect('home')

def share_post(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        user_id = request.session['user_id']
        user = User.objects.get_user(user_id)
        shared_post_id = int(request.POST['post_id'])
        shared_post = Post.objects.get_post(shared_post_id)
        Post.objects.create_post({'content': shared_post.content, 'creator': user, 'shared': True, 'shared_post_id': shared_post_id})
        redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
        profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    return redirect('home')

def delete_post(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    id = int(request.POST['post_id'])
    post = Post.objects.get_post(id)
    if post.creator.id != int(request.session['user_id']):
        messages.error(request, 'You cannot delete a post which you have not created.', extra_tags='post')
        redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
        profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    Post.objects.delete_post(id)
    redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
    profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
    return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)

def add_comment(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        content = request.POST['content']
        post_id = request.POST['post_id']
        errors = Comment.objects.basic_validator({'content': content})
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='comment')
            return redirect('view_post', id=post_id)
        user = User.objects.get_user(int(request.session['user_id']))
        post = Post.objects.get_post(post_id)
        Comment.objects.create_comment({'content': content, 'user': user, 'post': post})
        return redirect('view_post', id=post_id)
    return redirect('home')

def delete_comment(request, id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    comment = Comment.objects.get(id=id)
    if comment.commentor.id != request.session['user_id']:
        messages.error(request, 'You cannot delete a comment which you have not created.', extra_tags='comment')
        return redirect('view_post', id=comment.post.id)
    Comment.objects.delete_comment(id)
    return redirect('view_post', id=comment.post.id)

def send_message(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        sender_id = request.session['user_id']
        recipient_id = request.POST['recipient_id']
        content = request.POST['content']
        errors = Message.objects.basic_validator({'content': content})
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='message')
            return redirect('home')
        Message.objects.send_message({'sender_id': sender_id, 'recipient_id': recipient_id, 'content': content})
        return redirect('home')
    return redirect('home')

def view_messages(request, friend_id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user_id = request.session['user_id']
    messages = Message.objects.get_messages({'user_id': user_id, 'friend_id': friend_id})
    friend = User.objects.get_user(friend_id)
    context = {
        'messages': messages,
        'friend': friend,
    }
    return render(request, 'messages.html', context)

def add_friend(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        friend_id = int(request.POST['friend_id'])
        user = User.objects.get(id=int(request.session['user_id']))
        friend = User.objects.get(id=friend_id)
        if friend in user.friends.all():
            messages.error(request, 'You are already friends with this user.', extra_tags='add_friend')
            return redirect('view_profile', id=friend_id)
        Friendship.objects.create_friendship({'friend_1': user, 'friend_2': friend})
        return redirect('view_profile', id=friend_id)
    return redirect('home')

def remove_friend(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        friend_id = int(request.POST['friend_id'])
        user = User.objects.get(id=int(request.session['user_id']))
        friend = User.objects.get(id=friend_id)
        if friend not in user.friends.all():
            messages.error(request, 'This user is not in your friends list.', extra_tags='remove_friend')
            return redirect('view_profile', id=friend_id)
        Friendship.objects.remove_friendship({'user_1': user.id, 'user_2': friend.id})
        return redirect('view_profile', id=friend_id)
    return redirect('home')
    
def edit_comment(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        comment_id = request.POST['comment_id']
        comment = Comment.objects.get(id=comment_id)
        if comment.commentor.id != int(request.session['user_id']):
            messages.error(request, 'You cannot edit a comment that you did not create.', extra_tags='edit_comment')
            return redirect('view_post', id=comment.post.id)
        content = request.POST['content']
        errors = Comment.objects.basic_validator({'content': content})
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='edit_comment')
            return redirect('view_post', id=comment.post.id)
        Comment.objects.update_comment(comment, content)
        return redirect('view_post', id=comment.post.id)
    return redirect('home')

def edit_post(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        post_id = int(request.POST['post_id'])
        post = Post.objects.get(id=post_id)
        if post.creator.id != int(request.session['user_id']):
            messages.error(request, 'You cannot edit a post that you did not create.', extra_tags='edit_post')
            return redirect('view_post', id=post_id)
        content = request.POST['content']
        errors = Post.objects.basic_validator({'content': content})
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='edit_post')
            return redirect('view_post', id=post_id)
        Post.objects.update_post(post, content)
        return redirect('view_post', id=post_id)
    return redirect('home')

def update_personal_details(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        user = User.objects.get(id=int(request.session['user_id']))
        data = {
            'user': user,
            'bio': request.POST.get('bio', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'workplace': request.POST.get('workplace', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'relationship_status': request.POST.get('relationship_status', '').strip(),
        }
        errors = PersonalDetails.objects.basic_validator(data)
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='update_personal_details')
            return redirect('edit_profile', id=user.id)
        PersonalDetails.objects.update_personal_details_record(data)
        return redirect('view_profile', id=user.id)
    return redirect('home')